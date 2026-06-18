#!/usr/bin/env python3
"""SMS Drip Campaign Engine — multi-step nurture sequences with branch logic and AI personalization."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
CAMPAIGN_NUMBER = os.getenv("CAMPAIGN_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
drip_campaigns = {}
subscribers = {}

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": CAMPAIGN_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception as e:
        app.logger.error(f"SMS failed: {e}")

@app.route("/drip/create", methods=["POST"])
def create_drip():
    data = request.get_json()
    did = f"DRIP-{int(time.time())}"
    drip_campaigns[did] = {"name": data.get("name"), "steps": data.get("steps", []), "created": time.time()}
    return jsonify({"drip_id": did}), 200

@app.route("/drip/<did>/subscribe", methods=["POST"])
def subscribe(did):
    data = request.get_json()
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
    payload = request.get_json()
    data = payload.get("data", {})
    if data.get("event_type") != "message.received" or data.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = data.get("from", {}).get("phone_number", "")
    text = data.get("text", "").strip().upper()
    if text == "STOP":
        subscribers.pop(from_number, None)
        send_sms(from_number, "Unsubscribed. Reply START to re-subscribe.")
    return jsonify({"status": "handled"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "campaigns": len(drip_campaigns), "subscribers": len(subscribers)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
