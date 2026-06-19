#!/usr/bin/env python3
"""SMS Appointment No-Show Predictor — AI predicts no-shows from SMS response patterns, triggers interventions."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
BOT_NUMBER = os.getenv("BOT_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
patients = {}  # phone -> {appointments, response_history, no_show_risk}

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

_start_ttl_cleanup(patients)


def call_inference(messages, max_tokens=200):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": BOT_NUMBER, "to": to, "text": text, "messaging_profile_id": os.getenv("MESSAGING_PROFILE_ID", "", timeout=10)}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

def predict_no_show(patient_data):
    messages = [{"role": "system", "content": "Predict no-show probability based on patient history. Return JSON: risk_score (0.0-1.0), risk_level (low/medium/high), factors (list of strings explaining why), intervention (string suggestion)."},
        {"role": "user", "content": json.dumps(patient_data)}]
    return call_inference(messages)

@app.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    phone = data.get("phone")
    if phone not in patients:
        patients[phone] = {"appointments": [], "response_history": [], "no_shows": 0, "shows": 0}
    patients[phone]["appointments"].append({**data, "status": "scheduled"})
    # Send confirmation and track response
    send_sms(phone, f"Your appointment is scheduled for {data.get('datetime', 'soon')}. Reply YES to confirm or RESCHEDULE to change.")
    patients[phone]["response_history"].append({"type": "confirmation_sent", "time": time.time()})
    return jsonify({"status": "scheduled"}), 200

@app.route("/predict", methods=["POST"])
def run_predictions():
    predictions = []
    for phone, patient in patients.items():
        upcoming = [a for a in patient["appointments"] if a.get("status") == "scheduled"]
        if not upcoming: continue
        try:
            result = json.loads(predict_no_show(patient))
            patient["no_show_risk"] = result.get("risk_score", 0.5)
            predictions.append({"phone": phone, **result})
            if result.get("risk_level") == "high":
                intervention = result.get("intervention", "We noticed you have an upcoming appointment. Need to reschedule?")
                send_sms(phone, intervention)
        except Exception:
            pass
    return jsonify({"predictions": predictions}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_sms():
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    p = data.get("payload", {})
    if data.get("event_type") != "message.received" or p.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = p.get("from", {}).get("phone_number", "")
    text = p.get("text", "").strip().upper()
    patient = patients.get(from_number)
    if not patient: return jsonify({"status": "unknown_patient"}), 200
    patient["response_history"].append({"type": "reply", "text": text, "time": time.time()})
    if "YES" in text:
        for appt in patient["appointments"]:
            if appt.get("status") == "scheduled":
                appt["status"] = "confirmed"
                break
        send_sms(from_number, "Confirmed! See you then.")
    elif "RESCHEDULE" in text:
        send_sms(from_number, "No problem. What day/time works better?")
    return jsonify({"status": "handled"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "patients": len(patients)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
