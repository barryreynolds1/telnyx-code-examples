#!/usr/bin/env python3
"""Hosted Messaging Campaign Manager — manage hosted messaging campaigns with subscriber opt-in/out tracking and delivery analytics."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
FROM_NUMBER = os.getenv("FROM_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
campaigns = {}
subscribers = {}
delivery_log = []

@app.route("/campaigns", methods=["POST"])
def create_campaign():
    data = request.get_json()
    cid = f"CAMP-{int(time.time())}"
    campaigns[cid] = {"id": cid, "name": data.get("name"), "message": data.get("message"),
        "status": "draft", "sent": 0, "delivered": 0, "failed": 0, "opted_out": 0,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    return jsonify({"campaign_id": cid, "campaign": campaigns[cid]}), 200

@app.route("/subscribers", methods=["POST"])
def add_subscribers():
    data = request.get_json()
    numbers = data.get("numbers", [])
    added = 0
    for num in numbers:
        if num not in subscribers:
            subscribers[num] = {"number": num, "status": "opted_in",
                "added": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            added += 1
    return jsonify({"added": added, "total": len(subscribers)}), 200

@app.route("/campaigns/<cid>/send", methods=["POST"])
def send_campaign(cid):
    campaign = campaigns.get(cid)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    active_subs = [s for s in subscribers.values() if s["status"] == "opted_in"]
    sent = 0
    failed = 0
    for sub in active_subs:
        try:
            resp = requests.post(f"{API}/messages", headers=headers,
                json={"from": FROM_NUMBER, "to": sub["number"], "text": campaign["message"],
                    "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
            if resp.ok:
                sent += 1
                delivery_log.append({"campaign": cid, "to": sub["number"], "status": "sent",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
            else:
                failed += 1
        except Exception:
            failed += 1
    campaign["sent"] = sent
    campaign["failed"] = failed
    campaign["status"] = "sent"
    return jsonify({"sent": sent, "failed": failed, "total_subscribers": len(active_subs)}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_messaging():
    payload = request.get_json()
    data = payload.get("data", {})
    if data.get("event_type") == "message.received" and data.get("direction") == "inbound":
        phone = data.get("from", {}).get("phone_number", "")
        text = data.get("text", "").strip().upper()
        if text in ("STOP", "UNSUBSCRIBE", "QUIT", "CANCEL"):
            if phone in subscribers:
                subscribers[phone]["status"] = "opted_out"
            requests.post(f"{API}/messages", headers=headers,
                json={"from": FROM_NUMBER, "to": phone, "text": "You have been unsubscribed. Reply START to re-subscribe.",
                    "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
            return jsonify({"status": "opted_out"}), 200
        elif text in ("START", "SUBSCRIBE", "YES"):
            subscribers[phone] = {"number": phone, "status": "opted_in",
                "added": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            requests.post(f"{API}/messages", headers=headers,
                json={"from": FROM_NUMBER, "to": phone, "text": "Welcome! You are now subscribed. Reply STOP to unsubscribe.",
                    "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
            return jsonify({"status": "opted_in"}), 200
    elif data.get("event_type") == "message.finalized":
        delivery_log.append({"to": data.get("to", {}).get("phone_number"),
            "status": data.get("status"), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return jsonify({"status": "ok"}), 200

@app.route("/subscribers", methods=["GET"])
def list_subscribers():
    active = sum(1 for s in subscribers.values() if s["status"] == "opted_in")
    return jsonify({"total": len(subscribers), "active": active,
        "opted_out": len(subscribers) - active}), 200

@app.route("/campaigns", methods=["GET"])
def list_campaigns():
    return jsonify({"campaigns": list(campaigns.values())}), 200

@app.route("/analytics", methods=["GET"])
def analytics():
    return jsonify({"total_sent": len(delivery_log),
        "by_status": {s: sum(1 for d in delivery_log if d.get("status") == s) for s in set(d.get("status", "") for d in delivery_log)}}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "campaigns": len(campaigns), "subscribers": len(subscribers)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
