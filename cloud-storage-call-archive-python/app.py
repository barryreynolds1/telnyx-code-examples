#!/usr/bin/env python3
"""Cloud Storage Call Archive — archive call recordings to Telnyx Cloud Storage with
searchable metadata.

Telnyx Cloud Storage is S3-compatible, so uploads use the AWS SDK (boto3) pointed at
the Telnyx S3 endpoint (`https://{region}.telnyxcloudstorage.com`, API key as both
access and secret key). The recording itself is downloaded from its Telnyx recording
URL over HTTPS, then stored in the bucket with its metadata attached to the object.
Docs: https://developers.telnyx.com/docs/cloud-storage/quick-start
"""
import os, json, time, telnyx
from urllib.parse import urlparse
import requests
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()
app = Flask(__name__)
# public_key (from the Portal) lets the SDK verify inbound webhook signatures.
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "call-archive")
REGION = os.getenv("TELNYX_STORAGE_REGION", "us-central-1")
ENDPOINT_URL = f"https://{REGION}.telnyxcloudstorage.com"

# S3-compatible client; the Telnyx API key is supplied as access key AND secret key.
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=TELNYX_API_KEY,
    aws_secret_access_key=TELNYX_API_KEY,
    region_name=REGION,
    config=Config(signature_version="s3v4"),
)

# In-memory metadata index for listing/search (use a database in production).
archive_index = []


def is_telnyx_url(url: str) -> bool:
    """Only Telnyx-owned https hosts may be fetched with the API key attached — this
    prevents both SSRF and leaking the bearer token to an attacker-supplied URL."""
    try:
        parts = urlparse(url or "")
    except ValueError:
        return False
    host = (parts.hostname or "").lower()
    return parts.scheme == "https" and (host == "telnyx.com" or host.endswith(".telnyx.com"))


@app.route("/buckets", methods=["POST"])
def create_bucket():
    """Create the archive bucket (idempotent)."""
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            app.logger.error("create_bucket failed: %s", e)
            return jsonify({"error": "could not create bucket"}), 502
    return jsonify({"status": "ready", "bucket": BUCKET_NAME}), 200


@app.route("/buckets", methods=["GET"])
def list_buckets():
    try:
        resp = s3.list_buckets()
    except ClientError as e:
        app.logger.error("list_buckets failed: %s", e)
        return jsonify({"error": "internal error"}), 502
    return jsonify({"buckets": [b["Name"] for b in resp.get("Buckets", [])]}), 200


@app.route("/archive", methods=["POST"])
def archive_recording():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    recording_url = data.get("recording_url")
    call_id = data.get("call_id", f"call-{int(time.time())}")
    metadata = data.get("metadata", {})
    if not recording_url:
        return jsonify({"error": "recording_url required"}), 400
    if not is_telnyx_url(recording_url):
        return jsonify({"error": "recording_url must be an https Telnyx URL"}), 400
    # 1) Download the recording from Telnyx (API key only sent to a Telnyx host).
    try:
        audio_resp = requests.get(recording_url, headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, timeout=30)
        audio_resp.raise_for_status()
    except Exception as e:
        app.logger.error("recording download failed: %s", e)
        return jsonify({"error": "Failed to download recording"}), 502
    # 2) Store it in the bucket with its metadata (S3 object metadata is string-valued).
    object_key = f"{time.strftime('%Y/%m/%d')}/{call_id}.mp3"
    try:
        s3.put_object(
            Bucket=BUCKET_NAME, Key=object_key, Body=audio_resp.content,
            ContentType="audio/mpeg",
            Metadata={str(k): str(v) for k, v in metadata.items()},
        )
    except ClientError as e:
        app.logger.error("archive upload failed: %s", e)
        return jsonify({"error": "could not store recording"}), 502
    entry = {"call_id": call_id, "object_key": object_key, "bucket": BUCKET_NAME,
             "size_bytes": len(audio_resp.content), "metadata": metadata,
             "archived_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    archive_index.append(entry)
    return jsonify({"status": "archived", "entry": entry}), 200


@app.route("/webhooks/recording", methods=["POST"])
def handle_recording_webhook():
    """Queue a recording for archival when Telnyx reports it saved. Call Control
    nests event fields under data.payload."""
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    body = request.get_json()
    if not body:
        return jsonify({"error": "invalid request body"}), 400
    data = body.get("data", {})
    p = data.get("payload", {})
    if data.get("event_type") == "call.recording.saved":
        recording_url = (p.get("recording_urls") or {}).get("mp3")
        if recording_url:
            archive_index.append({
                "call_id": p.get("call_control_id", ""), "recording_url": recording_url,
                "duration": p.get("recording_duration_millis"), "status": "queued",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
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
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
