#!/usr/bin/env python3
"""SMS Emergency Check-In — periodic wellness checks via SMS with escalation to emergency contacts."""
import os, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
# public_key (from the Portal) lets the SDK verify inbound webhook signatures.
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
CHECK_IN_NUMBER = os.getenv("CHECK_IN_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
monitored = {}  # phone -> {name, last_check_in, status, missed_count}

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

_start_ttl_cleanup(monitored)


def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": CHECK_IN_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

@app.route("/monitor", methods=["POST"])
def add_monitored():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    phone = data.get("phone")
    monitored[phone] = {"name": data.get("name", ""), "emergency_contact": data.get("emergency_contact", EMERGENCY_CONTACT),
        "last_check_in": time.time(), "status": "ok", "missed_count": 0}
    return jsonify({"status": "monitoring", "phone": phone}), 200

@app.route("/check-in/send", methods=["POST"])
def send_check_ins():
    results = []
    for phone, person in monitored.items():
        if person["status"] == "escalated": continue
        send_sms(phone, f"Hi {person['name']}! Just checking in. Reply OK to let us know you're safe.")
        person["status"] = "waiting"
        results.append({"phone": phone, "status": "sent"})
    return jsonify({"sent": results}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_reply():
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
    person = monitored.get(from_number)
    if not person: return jsonify({"status": "unknown"}), 200
    if "OK" in text or "GOOD" in text or "FINE" in text or "SAFE" in text:
        person["status"] = "ok"
        person["last_check_in"] = time.time()
        person["missed_count"] = 0
        send_sms(from_number, "Great to hear! Stay safe.")
    elif "HELP" in text or "SOS" in text:
        person["status"] = "escalated"
        ec = person.get("emergency_contact", EMERGENCY_CONTACT)
        send_sms(ec, f"ALERT: {person['name']} ({from_number}) sent a distress signal. Please check on them immediately.")
        send_sms(from_number, "Help is on the way. Your emergency contact has been notified.")
    return jsonify({"status": "handled"}), 200

@app.route("/check-in/escalate", methods=["POST"])
def escalate_missed():
    escalated = []
    for phone, person in monitored.items():
        if person["status"] == "waiting":
            person["missed_count"] += 1
            if person["missed_count"] >= 2:
                person["status"] = "escalated"
                ec = person.get("emergency_contact", EMERGENCY_CONTACT)
                send_sms(ec, f"ALERT: {person['name']} ({phone}) has not responded to {person['missed_count']} check-ins. Please verify they are safe.")
                escalated.append(phone)
    return jsonify({"escalated": escalated}), 200

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({"monitored": {p: {"name": m["name"], "status": m["status"], "missed": m["missed_count"]} for p, m in monitored.items()}}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "monitored": len(monitored)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
