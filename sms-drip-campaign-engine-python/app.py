#!/usr/bin/env python3
"""SMS Drip Campaign Engine — multi-step nurture sequences with branch logic and AI personalization."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
# public_key (from the Portal) lets the SDK verify inbound webhook signatures.
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
CAMPAIGN_NUMBER = os.getenv("CAMPAIGN_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
drip_campaigns = {}
subscribers = {}

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

_start_ttl_cleanup(drip_campaigns, subscribers)


def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": CAMPAIGN_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

@app.route("/drip/create", methods=["POST"])
def create_drip():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    did = f"DRIP-{int(time.time())}"
    drip_campaigns[did] = {"name": data.get("name"), "steps": data.get("steps", []), "created": time.time()}
    return jsonify({"drip_id": did}), 200

@app.route("/drip/<did>/subscribe", methods=["POST"])
def subscribe(did):
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    phone = data.get("phone")
    if did not in drip_campaigns:
        return jsonify({"error": "Campaign not found"}), 404
    subscribers[phone] = {"drip_id": did, "step": 0, "subscribed": time.time(), "data": data}
    steps = drip_campaigns[did]["steps"]
    if steps:
        send_sms(phone, steps[0].get("message", "Welcome!"))
    return jsonify({"status": "subscribed"}), 200

@app.route("/drip/advance", methods=["POST"])
def advance_all():
    advanced = 0
    for phone, sub in subscribers.items():
        drip = drip_campaigns.get(sub["drip_id"])
        if not drip: continue
        sub["step"] += 1
        if sub["step"] < len(drip["steps"]):
            step = drip["steps"][sub["step"]]
            send_sms(phone, step.get("message", ""))
            advanced += 1
    return jsonify({"advanced": advanced}), 200

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
    if text == "STOP":
        subscribers.pop(from_number, None)
        send_sms(from_number, "Unsubscribed. Reply START to re-subscribe.")
    return jsonify({"status": "handled"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "campaigns": len(drip_campaigns), "subscribers": len(subscribers)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
