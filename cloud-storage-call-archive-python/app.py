#!/usr/bin/env python3
"""Cloud Storage Call Archive — archive call recordings to Telnyx Cloud Storage with searchable metadata."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "call-archive")
API = "https://api.telnyx.com/v2"
STORAGE_API = "https://api.telnyx.com/v2/storage"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
archive_index = []

@app.route("/buckets", methods=["POST"])
def create_bucket():
    try:
        resp = requests.post(f"{STORAGE_API}/buckets", headers=headers,
            json={"name": BUCKET_NAME, "region": "us-central-1"}, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/buckets", methods=["GET"])
def list_buckets():
    try:
        resp = requests.get(f"{STORAGE_API}/buckets", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/archive", methods=["POST"])
def archive_recording():
    data = request.get_json()
    recording_url = data.get("recording_url")
    call_id = data.get("call_id", f"call-{int(time.time())}")
    metadata = data.get("metadata", {})
    if not recording_url:
        return jsonify({"error": "recording_url required"}), 400
    try:
        audio_resp = requests.get(recording_url, headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, timeout=30)
        audio_resp.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Failed to download recording: {e}"}), 500
    date_prefix = time.strftime("%Y/%m/%d")
    object_key = f"{date_prefix}/{call_id}.mp3"
    try:
        upload_resp = requests.put(
            f"{STORAGE_API}/buckets/{BUCKET_NAME}/{object_key}",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "audio/mpeg"},
            data=audio_resp.content, timeout=30)
        entry = {"call_id": call_id, "object_key": object_key, "bucket": BUCKET_NAME,
            "size_bytes": len(audio_resp.content), "metadata": metadata,
            "archived_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        archive_index.append(entry)
        return jsonify({"status": "archived", "entry": entry}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhooks/recording", methods=["POST"])
def handle_recording_webhook():
    payload = request.get_json()
    data = payload.get("data", {})
    if data.get("event_type") == "call.recording.saved":
        recording_url = data.get("recording_urls", {}).get("mp3")
        call_id = data.get("call_control_id", "")
        if recording_url:
            entry = {"call_id": call_id, "recording_url": recording_url,
                "duration": data.get("duration_secs"), "status": "queued",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            archive_index.append(entry)
    return jsonify({"status": "ok"}), 200

@app.route("/archive", methods=["GET"])
def list_archive():
    date = request.args.get("date")
    results = archive_index if not date else [a for a in archive_index if date in a.get("object_key", "")]
    return jsonify({"recordings": results[-50:], "total": len(results)}), 200

@app.route("/archive/search", methods=["GET"])
def search_archive():
    q = request.args.get("q", "").lower()
    results = [a for a in archive_index if q in json.dumps(a).lower()]
    return jsonify({"results": results[:20], "query": q}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "archived": len(archive_index), "bucket": BUCKET_NAME}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
