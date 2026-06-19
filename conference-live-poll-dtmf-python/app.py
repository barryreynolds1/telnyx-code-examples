#!/usr/bin/env python3
"""Conference Live Poll via DTMF — host asks a question, all conference participants vote by pressing 1-4, results tallied instantly."""
import os, json, base64, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
CONF_NUMBER = os.getenv("CONF_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
conferences = {}
active_polls = {}

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

_start_ttl_cleanup(conferences, active_polls)


@app.route("/conference/create", methods=["POST"])
def create_conference():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    cid = f"CONF-{int(time.time())}"
    conferences[cid] = {"name": data.get("name", "Meeting"), "participants": {}, "polls": []}
    return jsonify({"conference_id": cid}), 200

@app.route("/conference/<cid>/invite", methods=["POST"])
def invite(cid):
    conf = conferences.get(cid)
    if not conf: return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    numbers = data.get("numbers", [])
    for num in numbers:
        try:
            resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"to": num, "from": CONF_NUMBER, "connection_id": CONNECTION_ID, "client_state": base64.b64encode(json.dumps({"cid": cid}).encode()).decode()}, timeout=10)
            ccid = resp.json().get("data", {}).get("call_control_id")
            if ccid: conf["participants"][ccid] = {"number": num, "status": "ringing"}
        except Exception: pass
    return jsonify({"invited": len(numbers)}), 200

@app.route("/conference/<cid>/poll", methods=["POST"])
def start_poll(cid):
    conf = conferences.get(cid)
    if not conf: return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    poll_id = f"POLL-{int(time.time())}"
    poll = {"question": data.get("question"), "options": data.get("options", []), "votes": {}, "status": "active"}
    conf["polls"].append(poll)
    active_polls[cid] = poll
    q = poll["question"]
    opts = " ".join(f"Press {i+1} for {o}." for i, o in enumerate(poll["options"][:4]))
    for ccid, p in conf["participants"].items():
        if p["status"] == "joined":
            try: client.calls.actions.speak(ccid, payload=f"Poll: {q} {opts}", voice="female", language_code="en-US")
            except Exception: pass
    return jsonify({"poll_id": poll_id}), 200

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
    cs_raw = p.get("client_state", "")
    cs = {}
    if cs_raw:
        try: cs = json.loads(base64.b64decode(cs_raw))
        except Exception: pass
    cid = cs.get("cid")
    conf = conferences.get(cid) if cid else None
    if event_type == "call.answered" and conf:
        conf["participants"][ccid]["status"] = "joined"
        client.calls.actions.speak(ccid, payload=f"Welcome to {conf['name']}. You're connected.", voice="female", language_code="en-US")
        return jsonify({"status": "joined"}), 200
    elif event_type == "call.speak.ended" and conf:
        poll = active_polls.get(cid)
        if poll and poll["status"] == "active" and ccid not in poll["votes"]:
            client.calls.actions.gather(ccid, input_type="dtmf", timeout_secs=15, min_digits=1, max_digits=1)
        return jsonify({"status": "ok"}), 200
    elif event_type == "call.gather.ended" and conf:
        digits = p.get("digits", "")
        poll = active_polls.get(cid)
        if poll and poll["status"] == "active" and digits:
            poll["votes"][ccid] = int(digits) if digits.isdigit() else 0
            client.calls.actions.speak(ccid, payload="Vote recorded.", voice="female", language_code="en-US")
        return jsonify({"status": "voted"}), 200
    elif event_type == "call.hangup" and conf:
        if ccid in conf["participants"]:
            conf["participants"][ccid]["status"] = "left"
        return jsonify({"status": "left"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/conference/<cid>/results", methods=["GET"])
def poll_results(cid):
    conf = conferences.get(cid)
    if not conf: return jsonify({"error": "Not found"}), 404
    poll = active_polls.get(cid)
    if not poll: return jsonify({"message": "No active poll"}), 200
    tally = {}
    for vote in poll["votes"].values():
        idx = vote - 1
        if 0 <= idx < len(poll["options"]):
            opt = poll["options"][idx]
            tally[opt] = tally.get(opt, 0) + 1
    return jsonify({"question": poll["question"], "votes": len(poll["votes"]), "results": tally}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "conferences": len(conferences)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
