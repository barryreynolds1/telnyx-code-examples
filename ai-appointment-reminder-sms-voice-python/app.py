#!/usr/bin/env python3
"""AI Appointment Reminder — SMS first, voice call for non-responders, AI handles rescheduling."""

import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time

load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
FROM_NUMBER = os.getenv("FROM_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"

appointments = []  # {patient_name, phone, datetime, service, status, reminder_stage}
active_calls = {}


def encode_client_state(data):
    """Encode call context for Telnyx client_state round-trip."""
    import base64, json
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_client_state(event_data):
    """Decode client_state echoed back by Telnyx webhook."""
    import base64, json
    cs = event_data.get("client_state", "")
    if not cs:
        return {}
    try:
        return json.loads(base64.b64decode(cs))
    except Exception:
        return {}

def _start_ttl_cleanup(*stores, ttl_seconds=3600, interval=300):
    def _cleanup():
        while True:
            _ttl_time.sleep(interval)
            cutoff = _ttl_time.time() - ttl_seconds
            for store in stores:
                expired = [k for k, v in store.items()
                           if isinstance(v, dict) and v.get("_ts", _ttl_time.time()) < cutoff]
                for k in expired:
                    store.pop(k, None)
    threading.Thread(target=_cleanup, daemon=True).start()

_start_ttl_cleanup(active_calls)


SYSTEM_PROMPT = """You are a friendly appointment reminder assistant. You're calling to confirm an upcoming appointment.
If they want to reschedule, offer available times. If they confirm, thank them. If they cancel, acknowledge gracefully.
Keep responses under 2 sentences — this is a phone call."""

def call_inference(messages, max_tokens=150):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": FROM_NUMBER, "to": to, "text": text}, timeout=10)
    except requests.RequestException as e:
        app.logger.error("SMS failed: %s", e)

def place_reminder_call(appt):
    try:
        resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"to": appt["phone"], "from": FROM_NUMBER, "connection_id": CONNECTION_ID}, timeout=10)
        ccid = resp.json().get("data", {}).get("call_control_id")
        if ccid:
            active_calls[ccid] = {"appointment": appt, "conversation": [{"role": "system", "content": SYSTEM_PROMPT}]}
    except requests.RequestException as e:
        app.logger.error("Call failed: %s", e)

@app.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    appt = {**data, "status": "pending", "reminder_stage": "none"}
    appointments.append(appt)
    return jsonify({"status": "added", "total": len(appointments)}), 200

@app.route("/remind", methods=["POST"])
def trigger_reminders():
    results = []
    for appt in appointments:
        if appt["status"] != "pending": continue
        if appt["reminder_stage"] == "none":
            send_sms(appt["phone"], f"Hi {appt.get('patient_name', '')}! Reminder: your {appt.get('service', 'appointment')} is on {appt.get('datetime', 'soon')}. Reply CONFIRM, RESCHEDULE, or CANCEL.")
            appt["reminder_stage"] = "sms_sent"
            results.append({"phone": appt["phone"], "action": "sms_sent"})
        elif appt["reminder_stage"] == "sms_no_response":
            place_reminder_call(appt)
            appt["reminder_stage"] = "call_placed"
            results.append({"phone": appt["phone"], "action": "call_placed"})
    return jsonify({"reminders_sent": results}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_sms():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    if data.get("event_type") != "message.received" or data.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = data.get("from", {}).get("phone_number", "")
    text = data.get("text", "").strip().upper()
    appt = next((a for a in appointments if a["phone"] == from_number and a["status"] == "pending"), None)
    if not appt:
        return jsonify({"status": "no_appointment"}), 200
    if "CONFIRM" in text:
        appt["status"] = "confirmed"
        send_sms(from_number, f"Confirmed! See you on {appt.get('datetime', 'your appointment date')}.")
    elif "CANCEL" in text:
        appt["status"] = "cancelled"
        send_sms(from_number, "Your appointment has been cancelled. Reply anytime to rebook.")
    elif "RESCHEDULE" in text:
        appt["status"] = "rescheduling"
        send_sms(from_number, "No problem! What day and time work better for you?")
    else:
        msgs = [{"role": "system", "content": "Help this patient with their appointment. Current appointment: " + json.dumps(appt)}, {"role": "user", "content": text}]
        response = call_inference(msgs, max_tokens=200)
        send_sms(from_number, response)
    return jsonify({"status": "handled"}), 200

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    call = active_calls.get(ccid)
    if event_type == "call.answered" and call:
        appt = call["appointment"]
        greeting = f"Hi {appt.get('patient_name', 'there')}! This is a reminder about your {appt.get('service', 'appointment')} on {appt.get('datetime', 'soon')}. Can you confirm you'll be there?"
        client.calls.actions.speak(ccid, payload=greeting, voice="female", language_code="en-US")
        call["conversation"].append({"role": "assistant", "content": greeting})
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="I didn't catch that. Can you confirm your appointment?", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": speech})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        active_calls.pop(ccid, None)
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "appointments": len(appointments), "active_calls": len(active_calls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
