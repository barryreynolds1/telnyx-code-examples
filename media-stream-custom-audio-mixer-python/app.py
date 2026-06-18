#!/usr/bin/env python3
"""Media Stream Custom Audio Mixer — mix custom audio into live calls via WebSocket-based media streaming."""
import os, json, time, base64, asyncio
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
import requests
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
active_streams = {}
stream_log = []

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    data = payload.get("data", {})
    event_type = data.get("event_type")
    ccid = data.get("call_control_id")
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        try:
            requests.post(f"{API}/calls/{ccid}/actions/answer", headers=headers, json={}, timeout=10)
        except Exception:
            pass
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        try:
            requests.post(f"{API}/calls/{ccid}/actions/streaming_start", headers=headers,
                json={"stream_url": os.getenv("STREAM_WEBSOCKET_URL", "wss://your-server/stream"),
                    "stream_track": "both_tracks", "enable_dialogflow": False}, timeout=10)
            active_streams[ccid] = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "streaming"}
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"status": "streaming_started"}), 200
    elif event_type == "streaming.started":
        stream_log.append({"call_id": ccid, "event": "started", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "ok"}), 200
    elif event_type == "streaming.stopped":
        active_streams.pop(ccid, None)
        stream_log.append({"call_id": ccid, "event": "stopped", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "ok"}), 200
    elif event_type == "call.hangup":
        if ccid in active_streams:
            try:
                requests.post(f"{API}/calls/{ccid}/actions/streaming_stop", headers=headers, json={}, timeout=10)
            except Exception:
                pass
            active_streams.pop(ccid, None)
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/streams/<ccid>/inject", methods=["POST"])
def inject_audio(ccid):
    data = request.get_json()
    audio_url = data.get("audio_url")
    if audio_url:
        try:
            requests.post(f"{API}/calls/{ccid}/actions/playback_start", headers=headers,
                json={"audio_url": audio_url, "overlay": data.get("overlay", True)}, timeout=10)
            return jsonify({"status": "injecting", "audio": audio_url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "audio_url required"}), 400

@app.route("/streams", methods=["GET"])
def list_streams():
    return jsonify({"active_streams": active_streams, "count": len(active_streams)}), 200

@app.route("/stream-log", methods=["GET"])
def get_log():
    return jsonify({"log": stream_log[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active_streams": len(active_streams)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
