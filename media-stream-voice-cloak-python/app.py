#!/usr/bin/env python3
"""Media Stream Voice Cloak — real-time voice modification via media streaming API. Apply pitch shift, echo, or anonymization."""
import os, json, time, base64, struct
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
API = "https://api.telnyx.com/v2"
import requests
import threading, time as _ttl_time
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
active_cloaks = {}

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

_start_ttl_cleanup(active_cloaks)

cloak_log = []

EFFECTS = {
    "deep": {"description": "Lower pitch by 30%", "pitch_shift": -0.3},
    "high": {"description": "Raise pitch by 40%", "pitch_shift": 0.4},
    "anonymous": {"description": "Robotic anonymization", "pitch_shift": -0.2, "modulation": True},
    "echo": {"description": "Add subtle echo", "echo_delay_ms": 50},
    "none": {"description": "No modification", "pitch_shift": 0},
}

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    event_type = data.get("event_type")
    ccid = data.get("call_control_id")
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        requests.post(f"{API}/calls/{ccid}/actions/answer", headers=headers, json={}, timeout=10)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        effect = active_cloaks.get(ccid, {}).get("effect", "anonymous")
        try:
            requests.post(f"{API}/calls/{ccid}/actions/streaming_start", headers=headers,
                json={"stream_url": os.getenv("STREAM_WEBSOCKET_URL", "wss://your-server/stream", timeout=10),
                    "stream_track": "inbound_track"}, timeout=10)
            active_cloaks[ccid] = {"effect": effect, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        except Exception:
            pass
        return jsonify({"status": "cloaking"}), 200
    elif event_type == "call.hangup":
        cloak = active_cloaks.pop(ccid, None)
        if cloak:
            cloak_log.append({"call_id": ccid, "effect": cloak.get("effect"), "ended": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/cloak/<ccid>", methods=["POST"])
def set_cloak(ccid):
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    effect = data.get("effect", "anonymous")
    if effect not in EFFECTS:
        return jsonify({"error": f"Unknown effect. Available: {list(EFFECTS.keys())}"}), 400
    active_cloaks[ccid] = {"effect": effect, "config": EFFECTS[effect],
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    return jsonify({"status": "effect_set", "effect": effect, "config": EFFECTS[effect]}), 200

@app.route("/effects", methods=["GET"])
def list_effects():
    return jsonify({"effects": EFFECTS}), 200

@app.route("/active", methods=["GET"])
def list_active():
    return jsonify({"active": active_cloaks}), 200

@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({"log": cloak_log[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active": len(active_cloaks)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
