#!/usr/bin/env python3
"""Video Webinar Recording Manager — manage video room webinars with automatic recording, transcription, and clip extraction."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
API = "https://api.telnyx.com/v2"
INFERENCE_URL = f"{API}/ai/chat/completions"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
webinars = {}
recordings = []

@app.route("/webinars", methods=["POST"])
def create_webinar():
    data = request.get_json()
    try:
        resp = requests.post(f"{API}/rooms", headers=headers,
            json={"unique_name": data.get("title", f"webinar-{int(time.time())}"),
                "max_participants": data.get("max_participants", 100),
                "enable_recording": True}, timeout=15)
        result = resp.json()
        room_id = result.get("data", {}).get("id")
        if room_id:
            webinars[room_id] = {"id": room_id, "title": data.get("title"),
                "host": data.get("host"), "scheduled": data.get("scheduled"),
                "status": "scheduled", "recording_id": None,
                "created": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        return jsonify(result), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webinars/<room_id>/recordings", methods=["GET"])
def get_recordings(room_id):
    try:
        resp = requests.get(f"{API}/rooms/{room_id}/recordings", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/recordings/<recording_id>/transcribe", methods=["POST"])
def transcribe_recording(recording_id):
    data = request.get_json()
    transcript = data.get("transcript", "")
    if not transcript:
        return jsonify({"error": "transcript text required (paste recording transcript)"}), 400
    try:
        result = requests.post(INFERENCE_URL, headers=headers,
            json={"model": AI_MODEL, "messages": [
                {"role": "system", "content": "Generate webinar summary. Return JSON: title (string), summary (2 paragraphs), key_points (list of strings), action_items (list), q_and_a (list of {question, answer}), duration_estimate (string)."},
                {"role": "user", "content": transcript[:4000]}], "max_tokens": 600, "temperature": 0.3}, timeout=25)
        summary = json.loads(result.json()["choices"][0]["message"]["content"])
        summary["recording_id"] = recording_id
        summary["processed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        recordings.append(summary)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webinars", methods=["GET"])
def list_webinars():
    return jsonify({"webinars": list(webinars.values())}), 200

@app.route("/recordings", methods=["GET"])
def list_processed():
    return jsonify({"recordings": recordings[-20:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "webinars": len(webinars), "recordings": len(recordings)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
