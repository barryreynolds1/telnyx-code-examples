#!/usr/bin/env python3
"""Toll-Free SMS Campaign Manager — manage toll-free verification and send compliant campaigns."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TOLL_FREE_NUMBER = os.getenv("TOLL_FREE_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID")
campaigns = {}

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

_start_ttl_cleanup(campaigns)

opt_outs = set()

@app.route("/campaigns", methods=["POST"])
def create_campaign():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    cid = f"TFC-{int(time.time())}"
    campaigns[cid] = {"name": data.get("name"), "message": data.get("message"), "contacts": data.get("contacts", []),
        "status": "created", "sent": 0, "delivered": 0, "failed": 0, "opted_out": 0}
    return jsonify({"campaign_id": cid}), 200

@app.route("/campaigns/<cid>/send", methods=["POST"])
def send_campaign(cid):
    campaign = campaigns.get(cid)
    if not campaign: return jsonify({"error": "Not found"}), 404
    for contact in campaign["contacts"]:
        if contact in opt_outs:
            campaign["opted_out"] += 1
            continue
        try:
            msg = campaign["message"] + "\nReply STOP to unsubscribe."
            requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"from": TOLL_FREE_NUMBER, "to": contact, "text": msg, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
            campaign["sent"] += 1
        except Exception:
            campaign["failed"] += 1
    campaign["status"] = "sent"
    return jsonify({"sent": campaign["sent"], "failed": campaign["failed"], "opted_out": campaign["opted_out"]}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_reply():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    if data.get("event_type") != "message.received" or data.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = data.get("from", {}).get("phone_number", "")
    text = data.get("text", "").strip().upper()
    if text == "STOP":
        opt_outs.add(from_number)
        try:
            requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"from": TOLL_FREE_NUMBER, "to": from_number, "text": "You have been unsubscribed. Reply START to re-subscribe.", "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
        except Exception:
            pass
    elif text == "START":
        opt_outs.discard(from_number)
    return jsonify({"status": "handled"}), 200

@app.route("/verification/status", methods=["GET"])
def verification_status():
    try:
        resp = requests.get("https://api.telnyx.com/v2/phone_numbers/" + TOLL_FREE_NUMBER, headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, timeout=10)
        return jsonify(resp.json().get("data", {})), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "campaigns": len(campaigns), "opt_outs": len(opt_outs)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
