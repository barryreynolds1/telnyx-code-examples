#!/usr/bin/env python3
"""Call Analytics Dashboard API — pull CDRs and build usage analytics."""
import os, json, time, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")

@app.route("/analytics/calls", methods=["GET"])
def call_analytics():
    days = int(request.args.get("days", 7))
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    try:
        resp = requests.get("https://api.telnyx.com/v2/reports/call_events", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            params={"filter[start_time][gte]": start, "page[size]": 250}, timeout=30)
        if resp.ok:
            data = resp.json().get("data", [])
            total = len(data)
            inbound = sum(1 for d in data if d.get("direction") == "inbound")
            outbound = total - inbound
            durations = [d.get("duration_secs", 0) for d in data if d.get("duration_secs")]
            avg_duration = sum(durations) / max(len(durations), 1)
            return jsonify({"period_days": days, "total_calls": total, "inbound": inbound, "outbound": outbound,
                "avg_duration_secs": round(avg_duration, 1), "total_minutes": round(sum(durations) / 60, 1)}), 200
        return jsonify({"error": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics/numbers", methods=["GET"])
def number_analytics():
    try:
        resp = requests.get("https://api.telnyx.com/v2/phone_numbers", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            params={"page[size]": 250}, timeout=15)
        if resp.ok:
            numbers = resp.json().get("data", [])
            by_status = {}
            for n in numbers:
                status = n.get("status", "unknown")
                by_status[status] = by_status.get(status, 0) + 1
            return jsonify({"total_numbers": len(numbers), "by_status": by_status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Failed"}), 500

@app.route("/analytics/messaging", methods=["GET"])
def messaging_analytics():
    try:
        resp = requests.get("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            params={"page[size]": 100}, timeout=15)
        if resp.ok:
            msgs = resp.json().get("data", [])
            sent = sum(1 for m in msgs if m.get("direction") == "outbound")
            received = sum(1 for m in msgs if m.get("direction") == "inbound")
            return jsonify({"recent_messages": len(msgs), "sent": sent, "received": received}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Failed"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
