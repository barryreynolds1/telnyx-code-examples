#!/usr/bin/env python3
"""Storage Voicemail Archive — record voicemails to Telnyx Cloud Storage with search."""
import os
import boto3, json, time, requests, telnyx
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



def encode_client_state(data):
    """Encode call context for Telnyx client_state round-trip."""
    import base64, json
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_client_state(event_data):
    """Decode client_state echoed back by Telnyx webhook."""
    import base64, json
    cs = event_data.get("client_state", "")
    if not cs:
        return {}
    try:
        return json.loads(base64.b64decode(cs))
    except Exception:
        return {}

def get_s3_client():
    """Get boto3 S3 client configured for Telnyx Cloud Storage."""
    import boto3
    return boto3.client(
        "s3",
        endpoint_url="https://storage.telnyx.com",
        aws_access_key_id=TELNYX_API_KEY,
        aws_secret_access_key=TELNYX_API_KEY,
        region_name="us-central-1",
    )

def upload_to_storage(key, data, content_type="audio/mpeg"):
    """Upload a file to Telnyx Cloud Storage (S3-compatible)."""
    s3 = get_s3_client()
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=data, ContentType=content_type)
    return f"https://{BUCKET_NAME}.storage.telnyx.com/{key}"

def download_from_storage(key):
    """Download a file from Telnyx Cloud Storage (S3-compatible)."""
    s3 = get_s3_client()
    resp = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return resp["Body"].read()
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
                upload_to_storage(key, data)
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
