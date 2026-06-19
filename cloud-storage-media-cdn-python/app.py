#!/usr/bin/env python3
"""Cloud Storage Media CDN — store and serve voice media (IVR prompts, hold music,
announcements, voicemail greetings) on Telnyx Cloud Storage.

Telnyx Cloud Storage is S3-compatible, so this talks to it with the AWS SDK (boto3)
pointed at the Telnyx S3 endpoint — not the REST API. Two Telnyx-specific details:

  1. Endpoint is region-scoped:  https://{region}.telnyxcloudstorage.com
  2. Auth uses your Telnyx API key as BOTH the access key and the secret key.

Media is served with presigned GET URLs you can drop straight into a TeXML <Play>
verb or a Call Control `playback_audio` command. The bucket itself is the source of
truth, so there is no server-side catalog to keep in sync.

Docs: https://developers.telnyx.com/docs/cloud-storage/quick-start
"""
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()
app = Flask(__name__)

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "media-cdn")
# Region selects the endpoint host, e.g. us-central-1 -> us-central-1.telnyxcloudstorage.com
REGION = os.getenv("TELNYX_STORAGE_REGION", "us-central-1")
ENDPOINT_URL = f"https://{REGION}.telnyxcloudstorage.com"
# How long presigned playback URLs stay valid (seconds).
PRESIGN_TTL = int(os.getenv("PRESIGN_TTL_SECONDS", "3600"))

# S3-compatible client. The Telnyx API key is supplied as access key AND secret key.
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=TELNYX_API_KEY,
    aws_secret_access_key=TELNYX_API_KEY,
    region_name=REGION,
    config=Config(signature_version="s3v4"),
)

# Logical folders within the bucket (object key prefixes).
CATEGORIES = {
    "ivr_prompts": "IVR greeting and menu prompts",
    "hold_music": "Hold music tracks",
    "announcements": "System announcements",
    "voicemail_greetings": "Voicemail greeting templates",
}


def presign(key: str) -> str:
    """Return a time-limited GET URL for an object — safe to hand to a call flow."""
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET_NAME, "Key": key}, ExpiresIn=PRESIGN_TTL
    )


@app.route("/setup", methods=["POST"])
def setup_bucket():
    """Create the media bucket (idempotent)."""
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        # Re-running setup is fine; only a real failure is an error.
        code = e.response.get("Error", {}).get("Code", "")
        if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            app.logger.error("create_bucket failed: %s", e)
            return jsonify({"error": "could not create bucket"}), 502
    return jsonify({"status": "ready", "bucket": BUCKET_NAME, "categories": list(CATEGORIES)}), 200


@app.route("/upload", methods=["POST"])
def upload_media():
    """Upload a media file. The client sends the bytes directly (multipart/form-data),
    so the server never fetches an arbitrary URL — no SSRF surface."""
    category = request.form.get("category", "ivr_prompts")
    name = request.form.get("name")
    file = request.files.get("file")
    if not name or file is None:
        return jsonify({"error": "multipart fields 'file' and 'name' are required"}), 400
    if category not in CATEGORIES:
        return jsonify({"error": f"category must be one of {list(CATEGORIES)}"}), 400
    key = f"{category}/{name}"
    try:
        s3.upload_fileobj(
            file, BUCKET_NAME, key,
            ExtraArgs={"ContentType": file.mimetype or "application/octet-stream"},
        )
    except ClientError as e:
        app.logger.error("upload failed: %s", e)
        return jsonify({"error": "upload failed"}), 502
    return jsonify({"status": "uploaded", "key": key, "category": category, "url": presign(key)}), 200


@app.route("/media", methods=["GET"])
def list_media():
    """List stored media, optionally filtered to one category."""
    category = request.args.get("category")
    prefix = f"{category}/" if category else ""
    try:
        resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    except ClientError as e:
        app.logger.error("list_objects failed: %s", e)
        return jsonify({"error": "could not list media"}), 502
    items = [
        {"key": o["Key"], "size_bytes": o["Size"], "last_modified": o["LastModified"].isoformat()}
        for o in resp.get("Contents", [])
    ]
    return jsonify({"media": items, "count": len(items)}), 200


@app.route("/media/<category>/<name>", methods=["GET"])
def get_media_url(category, name):
    """Return a presigned playback URL for a single object."""
    key = f"{category}/{name}"
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
    except ClientError:
        return jsonify({"error": "not found"}), 404
    return jsonify({"key": key, "url": presign(key), "expires_in": PRESIGN_TTL}), 200


@app.route("/ivr-config", methods=["GET"])
def ivr_config():
    """Presigned URLs for the prompt and hold-music sets, ready to drop into a call flow."""
    try:
        def urls_for(cat):
            resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{cat}/")
            return [presign(o["Key"]) for o in resp.get("Contents", [])]

        return jsonify({
            "ivr_prompts": urls_for("ivr_prompts"),
            "hold_music": urls_for("hold_music"),
            "usage": "Use these presigned URLs in a TeXML <Play> verb or Call Control playback_audio command.",
        }), 200
    except ClientError as e:
        app.logger.error("ivr_config failed: %s", e)
        return jsonify({"error": "internal error"}), 502


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bucket": BUCKET_NAME, "endpoint": ENDPOINT_URL}), 200


if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
