#!/usr/bin/env python3
"""Billing Anomaly Detector — monitor usage and billing for anomalies, alert on cost spikes and unusual patterns."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", "")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
alerts = []
baselines = {"daily_cost": 50.0, "daily_calls": 500, "daily_messages": 1000,
    "spike_threshold": 2.0, "drop_threshold": 0.3}

@app.route("/config", methods=["POST"])
def set_baselines():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    baselines.update(data)
    return jsonify({"baselines": baselines}), 200

@app.route("/config", methods=["GET"])
def get_baselines():
    return jsonify({"baselines": baselines}), 200

@app.route("/check", methods=["POST"])
def run_anomaly_check():
    anomalies = []
    try:
        today = time.strftime("%Y-%m-%d")
        resp = requests.get(f"{API}/reports/cdrs", headers=headers,
            params={"filter[start_date]": today, "filter[end_date]": today, "page[size]": 250}, timeout=30)
        cdrs = resp.json().get("data", [])
        daily_cost = sum(float(c.get("cost", 0)) for c in cdrs)
        daily_calls = len(cdrs)
        if daily_cost > baselines["daily_cost"] * baselines["spike_threshold"]:
            anomalies.append({"type": "cost_spike", "severity": "high",
                "current": round(daily_cost, 2), "baseline": baselines["daily_cost"],
                "ratio": round(daily_cost / max(baselines["daily_cost"], 0.01), 1)})
        if daily_calls > baselines["daily_calls"] * baselines["spike_threshold"]:
            anomalies.append({"type": "call_volume_spike", "severity": "medium",
                "current": daily_calls, "baseline": baselines["daily_calls"]})
        if daily_calls < baselines["daily_calls"] * baselines["drop_threshold"] and daily_calls > 0:
            anomalies.append({"type": "call_volume_drop", "severity": "medium",
                "current": daily_calls, "baseline": baselines["daily_calls"]})
        high_cost = [c for c in cdrs if float(c.get("cost", 0)) > 1.0]
        if high_cost:
            anomalies.append({"type": "expensive_calls", "severity": "low",
                "count": len(high_cost), "total_cost": round(sum(float(c.get("cost", 0)) for c in high_cost), 2)})
    except Exception as e:
        anomalies.append({"type": "check_failed", "error": str(e)})
    if anomalies:
        alert = {"anomalies": anomalies, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        alerts.append(alert)
        if ALERT_WEBHOOK:
            try:
                requests.post(ALERT_WEBHOOK, json={"text": f"Billing anomaly detected: {json.dumps(anomalies, timeout=10)}"}, timeout=10)
            except Exception:
                pass
    return jsonify({"anomalies": anomalies, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}), 200

@app.route("/balance", methods=["GET"])
def check_balance():
    try:
        resp = requests.get(f"{API}/balance", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/alerts", methods=["GET"])
def list_alerts():
    return jsonify({"alerts": alerts[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "alerts": len(alerts), "baselines": baselines}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
