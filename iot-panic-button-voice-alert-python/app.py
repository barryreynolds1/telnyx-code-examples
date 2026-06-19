#!/usr/bin/env python3
"""IoT Panic Button Voice Alert — IoT device triggers SIM-based alert, system calls emergency contacts with location and status."""
import os, json, base64, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
ALERT_NUMBER = os.getenv("ALERT_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
alerts = []
devices = {"DEV-001": {"name": "Warehouse A Panic Button", "location": "Building 3, Floor 1", "contacts": ["+15551234567", "+15559876543"]},
    "DEV-002": {"name": "Parking Lot B", "location": "North lot, near entrance", "contacts": ["+15551234567"]}}

@app.route("/alert", methods=["POST"])
def trigger_alert():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    device_id = data.get("device_id")
    device = devices.get(device_id)
    if not device: return jsonify({"error": "Unknown device"}), 404
    alert_id = f"ALERT-{int(time.time())}"
    alert = {"id": alert_id, "device_id": device_id, "device_name": device["name"], "location": device["location"],
        "triggered": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "active", "calls_made": []}
    for contact in device["contacts"]:
        try:
            resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"to": contact, "from": ALERT_NUMBER, "connection_id": CONNECTION_ID,
                    "client_state": base64.b64encode(json.dumps({"alert_id": alert_id, "device": device["name"], "location": device["location"]}).encode()).decode()}, timeout=10)
            alert["calls_made"].append({"contact": contact, "status": "calling"})
        except Exception:
            alert["calls_made"].append({"contact": contact, "status": "failed"})
        try:
            requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"from": ALERT_NUMBER, "to": contact, "text": f"PANIC ALERT: {device['name']} at {device['location']}. Alert ID: {alert_id}. Respond immediately."}, timeout=10)
        except Exception: pass
    alerts.append(alert)
    return jsonify({"alert_id": alert_id, "contacts_notified": len(device["contacts"])}), 200

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
    event_type = payload.get("data", {}).get("event_type")
    data = payload.get("data", {})
    p = data.get("payload", {})
    ccid = p.get("call_control_id")
    cs_raw = p.get("client_state", "")
    cs = {}
    if cs_raw:
        try: cs = json.loads(base64.b64decode(cs_raw))
        except Exception: pass
    if event_type == "call.answered":
        device = cs.get("device", "unknown device")
        location = cs.get("location", "unknown location")
        client.calls.actions.speak(ccid, payload=f"Emergency alert! Panic button activated at {device}, location: {location}. Press 1 to acknowledge, 2 to escalate to emergency services.", voice="female", language_code="en-US")
        return jsonify({"status": "alerting"}), 200
    elif event_type == "call.speak.ended":
        client.calls.actions.gather(ccid, input_type="dtmf", timeout_secs=15, min_digits=1, max_digits=1)
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended":
        digits = p.get("digits", "")
        if digits == "1":
            client.calls.actions.speak(ccid, payload="Alert acknowledged. Dispatch team notified. Stay safe.", voice="female", language_code="en-US")
        elif digits == "2":
            client.calls.actions.speak(ccid, payload="Escalating to emergency services. Please stay on the line.", voice="female", language_code="en-US")
        return jsonify({"status": "acknowledged"}), 200
    elif event_type == "call.hangup":
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/devices", methods=["POST"])
def register_device():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    did = data.get("device_id", f"DEV-{int(time.time())}")
    devices[did] = {"name": data.get("name"), "location": data.get("location"), "contacts": data.get("contacts", [])}
    return jsonify({"device_id": did}), 200

@app.route("/alerts", methods=["GET"])
def list_alerts():
    return jsonify({"alerts": alerts[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    active = sum(1 for a in alerts if a.get("status") == "active")
    return jsonify({"status": "ok", "devices": len(devices), "active_alerts": active}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
