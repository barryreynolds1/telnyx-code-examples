#!/usr/bin/env python3
"""Call Recording AI Summarizer — record calls, then summarize and extract action items with AI."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
recordings = []

def call_inference(messages, max_tokens=500):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}, timeout=20)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type")
    data = payload.get("data", {})
    if event_type == "call.recording.saved":
        recording = {"recording_url": data.get("recording_urls", {}).get("mp3"), "call_control_id": data.get("call_control_id"),
            "duration": data.get("duration_secs"), "channels": data.get("channels"), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        recordings.append(recording)
        return jsonify({"status": "saved"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/summarize", methods=["POST"])
def summarize_recording():
    data = request.get_json()
    transcript = data.get("transcript", "")
    if not transcript:
        return jsonify({"error": "transcript required"}), 400
    msgs = [{"role": "system", "content": "Summarize this call recording transcript. Return JSON: summary (3-5 sentences), action_items (list of {owner, task, deadline_mentioned}), decisions_made (list), follow_up_needed (boolean), sentiment (positive/neutral/negative), topics_discussed (list), call_type (sales/support/internal/other)."},
        {"role": "user", "content": transcript}]
    result = call_inference(msgs)
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        parsed = {"summary": result}
    return jsonify(parsed), 200

@app.route("/recordings", methods=["GET"])
def list_recordings():
    return jsonify({"recordings": recordings[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "recordings": len(recordings)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
