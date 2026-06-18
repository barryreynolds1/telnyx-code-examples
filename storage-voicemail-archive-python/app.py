#!/usr/bin/env python3
"""Storage Voicemail Archive — record voicemails to Telnyx Cloud Storage with search."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
VOICEMAIL_NUMBER = os.getenv("VOICEMAIL_NUMBER")
voicemails = []

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="Please leave your message after the beep.", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended":
        client.calls.actions.record_start(ccid, format="mp3", channels="single", play_beep=True, max_length_secs=120)
        return jsonify({"status": "recording"}), 200
    elif event_type == "call.recording.saved":
        recording_url = data.get("recording_urls", {}).get("mp3", "")
        caller = data.get("from", {}).get("phone_number", "unknown") if isinstance(data.get("from"), dict) else data.get("from", "unknown")
        filename = f"voicemail-{int(time.time())}-{caller.replace('+','')}.mp3"
        if recording_url and STORAGE_BUCKET:
            try:
                audio = requests.get(recording_url, timeout=30).content
                requests.put(f"https://api.telnyx.com/v2/storage/buckets/{STORAGE_BUCKET}/{filename}",
                    headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "audio/mpeg"}, data=audio, timeout=30)
            except Exception as e:
                app.logger.error("Storage upload failed: %s", e)
        voicemails.append({"caller": caller, "filename": filename, "duration": data.get("duration_secs"), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "archived"}), 200
    elif event_type == "call.hangup":
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/voicemails", methods=["GET"])
def list_voicemails():
    return jsonify({"voicemails": voicemails[-50:]}), 200

@app.route("/voicemails/search", methods=["GET"])
def search_voicemails():
    caller = request.args.get("caller", "")
    results = [v for v in voicemails if caller in v.get("caller", "")]
    return jsonify({"results": results}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "voicemails": len(voicemails)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
