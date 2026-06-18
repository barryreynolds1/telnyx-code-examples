#!/usr/bin/env python3
"""Cloud Storage Media CDN — use Telnyx Cloud Storage as a CDN for IVR prompts, hold music, and voice assets."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "media-cdn")
STORAGE_API = "https://api.telnyx.com/v2/storage"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
media_catalog = {}

CATEGORIES = {"ivr_prompts": "IVR greeting and menu prompts",
    "hold_music": "Hold music tracks", "announcements": "System announcements",
    "voicemail_greetings": "Voicemail greeting templates"}

@app.route("/setup", methods=["POST"])
def setup_bucket():
    try:
        resp = requests.post(f"{STORAGE_API}/buckets", headers=headers,
            json={"name": BUCKET_NAME, "region": "us-central-1"}, timeout=15)
        for cat in CATEGORIES:
            media_catalog[cat] = []
        return jsonify({"status": "bucket_created", "bucket": BUCKET_NAME,
            "categories": list(CATEGORIES.keys())}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_media():
    data = request.get_json()
    category = data.get("category", "ivr_prompts")
    name = data.get("name")
    content_url = data.get("url")
    if not name:
        return jsonify({"error": "name required"}), 400
    object_key = f"{category}/{name}"
    if content_url:
        try:
            audio = requests.get(content_url, timeout=30)
            requests.put(f"{STORAGE_API}/buckets/{BUCKET_NAME}/{object_key}",
                headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "audio/mpeg"},
                data=audio.content, timeout=30)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    entry = {"name": name, "key": object_key, "category": category,
        "cdn_url": f"https://storage.telnyx.com/{BUCKET_NAME}/{object_key}",
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    if category not in media_catalog:
        media_catalog[category] = []
    media_catalog[category].append(entry)
    return jsonify({"status": "uploaded", "entry": entry}), 200

@app.route("/media", methods=["GET"])
def list_media():
    category = request.args.get("category")
    if category:
        return jsonify({"media": media_catalog.get(category, []), "category": category}), 200
    return jsonify({"catalog": {k: len(v) for k, v in media_catalog.items()}}), 200

@app.route("/media/<category>/<name>", methods=["GET"])
def get_media_url(category, name):
    items = media_catalog.get(category, [])
    for item in items:
        if item["name"] == name:
            return jsonify({"url": item["cdn_url"], "item": item}), 200
    return jsonify({"error": "Not found"}), 404

@app.route("/ivr-config", methods=["GET"])
def ivr_config():
    prompts = media_catalog.get("ivr_prompts", [])
    hold = media_catalog.get("hold_music", [])
    return jsonify({"ivr_prompts": [p["cdn_url"] for p in prompts],
        "hold_music": [h["cdn_url"] for h in hold],
        "usage": "Use these URLs in your TeXML Play or Call Control playback_audio commands"}), 200

@app.route("/health", methods=["GET"])
def health():
    total = sum(len(v) for v in media_catalog.values())
    return jsonify({"status": "ok", "total_media": total, "bucket": BUCKET_NAME}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
