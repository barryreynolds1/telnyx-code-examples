#!/usr/bin/env python3
"""SMS Keyword Auto-Responder — keyword-triggered responses with match analytics."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
BOT_NUMBER = os.getenv("BOT_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")

keywords = {
    "HOURS": {"response": "We're open Mon-Fri 9am-6pm ET, Sat 10am-4pm. Closed Sundays.", "count": 0},
    "MENU": {"response": "View our full menu at https://example.com/menu", "count": 0},
    "PRICE": {"response": "Pricing starts at $9.99/mo. Visit https://example.com/pricing for details.", "count": 0},
    "HELP": {"response": "Commands: HOURS, MENU, PRICE, LOCATION, STOP. Reply with a keyword!", "count": 0},
    "LOCATION": {"response": "123 Main St, Suite 100, New York, NY 10001. Map: https://maps.example.com", "count": 0},
    "STOP": {"response": "You've been unsubscribed. Reply START to re-subscribe.", "count": 0},
}
message_log = []

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": BOT_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

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
    message_log.append({"from": from_number, "text": text, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    matched = False
    for keyword, config in keywords.items():
        if keyword in text:
            send_sms(from_number, config["response"])
            config["count"] += 1
            matched = True
            break
    if not matched:
        send_sms(from_number, "Sorry, I didn't understand. Reply HELP for available commands.")
    return jsonify({"status": "handled", "matched": matched}), 200

@app.route("/keywords", methods=["GET"])
def list_keywords():
    return jsonify({"keywords": {k: {"response": v["response"], "hits": v["count"]} for k, v in keywords.items()}}), 200

@app.route("/keywords", methods=["POST"])
def add_keyword():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    keyword = data.get("keyword", "").upper()
    response = data.get("response", "")
    keywords[keyword] = {"response": response, "count": 0}
    return jsonify({"status": "added", "keyword": keyword}), 200

@app.route("/analytics", methods=["GET"])
def analytics():
    total = sum(v["count"] for v in keywords.values())
    return jsonify({"total_matches": total, "by_keyword": {k: v["count"] for k, v in keywords.items()}, "recent_messages": len(message_log)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "keywords": len(keywords), "messages": len(message_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
