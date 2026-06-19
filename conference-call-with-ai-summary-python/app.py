#!/usr/bin/env python3
"""Conference Call with AI Summary — multi-party conference with transcription and AI post-call summary."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
CONFERENCE_NUMBER = os.getenv("CONFERENCE_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
conferences = {}
# Maps a call's call_control_id -> the conf_id it belongs to, so transcription
# events are appended only to that call's conference (no cross-contamination).
call_to_conf = {}

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

_start_ttl_cleanup(conferences, call_to_conf)


def call_inference(messages, max_tokens=500):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.3}, timeout=20)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/conference/create", methods=["POST"])
def create_conference():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    conf_id = f"CONF-{int(time.time())}"
    conferences[conf_id] = {"name": data.get("name", "Meeting"), "participants": [], "transcript": [], "started": time.time(), "status": "active"}
    return jsonify({"conference_id": conf_id}), 200

@app.route("/conference/<conf_id>/invite", methods=["POST"])
def invite_participant(conf_id):
    conf = conferences.get(conf_id)
    if not conf: return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    number = data.get("number")
    try:
        resp = requests.post("https://api.telnyx.com/v2/conferences", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"name": conf_id, "call_control_id": "", "beep_enabled": "on_enter"}, timeout=10)
        conf["participants"].append(number)
        return jsonify({"status": "invited"}), 200
    except Exception:
        app.logger.exception("Failed to invite participant to conference %s", conf_id)
        return jsonify({"error": "could not invite participant"}), 500

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    p = data.get("payload", {})
    event_type = data.get("event_type")
    ccid = p.get("call_control_id")
    if event_type == "call.initiated" and p.get("direction") == "incoming":
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        # Record which conference this call belongs to. Conference events carry the
        # conference reference as its name, which equals our conf_id.
        conf_id = p.get("conference_id") or p.get("conference_name") or p.get("name")
        if ccid and conf_id:
            call_to_conf[ccid] = conf_id
        client.calls.actions.speak(ccid, payload="Welcome to the conference. You are being connected.", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.transcription":
        text = p.get("transcription_data", {}).get("transcript", "")
        if text:
            # Append only to the conference this call belongs to — never to all of them.
            conf_id = p.get("conference_id") or p.get("conference_name") or call_to_conf.get(ccid)
            conf = conferences.get(conf_id) if conf_id else None
            if conf and conf["status"] == "active":
                conf["transcript"].append({"text": text, "time": time.time()})
        return jsonify({"status": "ok"}), 200
    elif event_type == "call.hangup":
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/conference/<conf_id>/summary", methods=["GET"])
def get_summary(conf_id):
    conf = conferences.get(conf_id)
    if not conf: return jsonify({"error": "Not found"}), 404
    if not conf["transcript"]: return jsonify({"summary": "No transcript available"}), 200
    full_transcript = " ".join(t["text"] for t in conf["transcript"])
    msgs = [{"role": "system", "content": "Summarize this conference call. Return JSON: summary (3-5 sentences), action_items (list), decisions_made (list), participants_identified (list), duration_topics (list of {topic, approximate_minutes})."},
        {"role": "user", "content": full_transcript}]
    summary = call_inference(msgs)
    return jsonify({"conference": conf_id, "summary": summary, "transcript_length": len(conf["transcript"])}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "conferences": len(conferences)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
