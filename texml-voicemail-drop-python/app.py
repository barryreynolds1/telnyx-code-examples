#!/usr/bin/env python3
"""TeXML Voicemail Drop — leave pre-recorded voicemails at scale via TeXML."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
FROM_NUMBER = os.getenv("FROM_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
VOICEMAIL_AUDIO_URL = os.getenv("VOICEMAIL_AUDIO_URL", "https://example.com/voicemail.mp3")
drops = []

@app.route("/drop", methods=["POST"])
def voicemail_drop():
    data = request.get_json()
    numbers = data.get("numbers", [])
    results = []
    for number in numbers:
        try:
            resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"to": number, "from": FROM_NUMBER, "connection_id": CONNECTION_ID, "answering_machine_detection": "detect_beep",
                    "webhook_url": request.host_url.rstrip("/") + "/webhooks/voice"}, timeout=10)
            ccid = resp.json().get("data", {}).get("call_control_id")
            drops.append({"number": number, "ccid": ccid, "status": "calling", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
            results.append({"number": number, "status": "initiated"})
        except Exception as e:
            results.append({"number": number, "status": "failed", "error": str(e)})
    return jsonify({"results": results, "total": len(results)}), 200

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    if event_type == "call.machine.detection.ended":
        result = payload.get("data", {}).get("result", "")
        if result in ("machine", "greeting_ended"):
            requests.post(f"https://api.telnyx.com/v2/calls/{ccid}/actions/playback_start",
                headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"audio_url": VOICEMAIL_AUDIO_URL}, timeout=10)
            for d in drops:
                if d.get("ccid") == ccid:
                    d["status"] = "message_playing"
        else:
            requests.post(f"https://api.telnyx.com/v2/calls/{ccid}/actions/hangup",
                headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json={}, timeout=10)
            for d in drops:
                if d.get("ccid") == ccid:
                    d["status"] = "human_answered_skipped"
        return jsonify({"status": "processed"}), 200
    elif event_type == "call.playback.ended":
        requests.post(f"https://api.telnyx.com/v2/calls/{ccid}/actions/hangup",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json={}, timeout=10)
        for d in drops:
            if d.get("ccid") == ccid:
                d["status"] = "delivered"
        return jsonify({"status": "delivered"}), 200
    elif event_type == "call.hangup":
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/drops", methods=["GET"])
def list_drops():
    return jsonify({"drops": drops[-100:], "total": len(drops)}), 200

@app.route("/health", methods=["GET"])
def health():
    delivered = sum(1 for d in drops if d.get("status") == "delivered")
    return jsonify({"status": "ok", "total_drops": len(drops), "delivered": delivered}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
