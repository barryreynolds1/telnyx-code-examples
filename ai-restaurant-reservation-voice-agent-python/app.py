#!/usr/bin/env python3
"""AI Restaurant Reservation Voice Agent — handles calls, checks availability, books tables, sends SMS confirmation."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
RESTAURANT_NUMBER = os.getenv("RESTAURANT_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
reservations = []
active_calls = {}

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


SYSTEM_PROMPT = """You are the AI host at Bella Cucina Italian Restaurant.
Hours: Tue-Sun 5pm-10pm, closed Monday. Capacity: 20 tables (2-8 guests).
Menu highlights: housemade pasta, wood-fired pizza, seasonal specials.
You can: book reservations, answer menu questions, provide hours/location, handle dietary requests.
Keep responses under 2 sentences. Be warm and professional."""

def call_inference(messages, max_tokens=150):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

DECISION_PROMPT = """You are a strict booking-state classifier for Bella Cucina restaurant.
Given the conversation so far, decide whether the MOST RECENT assistant turn actually FINALIZED a reservation (table booked and confirmed to the caller in this turn).
Asking for missing details, offering options, or saying nothing is booked yet all mean NOT finalized.
Return ONLY a JSON object, no prose, of the form:
{"confirmed": true|false, "details": {"time": "...", "party_size": ..., "date": "...", "name": "..."}}
Include in "details" only fields that were actually agreed. If not finalized, return {"confirmed": false, "details": {}}."""

def decide_reservation(conversation):
    """Structured decision: returns (confirmed: bool, details: dict). Never raises."""
    try:
        messages = [{"role": "system", "content": DECISION_PROMPT}] + \
            [m for m in conversation if m.get("role") in ("user", "assistant")]
        raw = call_inference(messages, max_tokens=200)
        decision = json.loads(raw)
        if not isinstance(decision, dict):
            return False, {}
        confirmed = decision.get("confirmed") is True
        details = decision.get("details") if isinstance(decision.get("details"), dict) else {}
        return confirmed, details
    except Exception as e:
        app.logger.error("Reservation decision failed: %s", e)
        return False, {}

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": RESTAURANT_NUMBER, "to": to, "text": text, "messaging_profile_id": os.getenv("MESSAGING_PROFILE_ID", "", timeout=10)}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
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
    event_type = data.get("event_type")
    ccid = p.get("call_control_id")
    call = active_calls.get(ccid)
    if event_type == "call.initiated" and p.get("direction") == "incoming":
        active_calls[ccid] = {"caller": p.get("from"), "conversation": [{"role": "system", "content": SYSTEM_PROMPT}]}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="Thank you for calling Bella Cucina! Would you like to make a reservation, or do you have a question?", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = p.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="Sorry, I didn't catch that. How can I help you?", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": speech})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        # Drive the real action from a strict structured decision, not the spoken prose.
        confirmed, details = decide_reservation(call["conversation"])
        if confirmed:
            reservation = {"caller": call["caller"], "booked_via": "voice",
                           "details": details, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            reservations.append(reservation)
            send_sms(call["caller"], "Your reservation at Bella Cucina is confirmed! Reply to this message if you need to change anything.")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        active_calls.pop(ccid, None)
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/reservations", methods=["GET"])
def list_reservations():
    return jsonify({"reservations": reservations[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "reservations": len(reservations), "active_calls": len(active_calls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
