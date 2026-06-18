#!/usr/bin/env python3
"""SMS Poll Voting System — text-to-vote polling with real-time results."""
import os, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
POLL_NUMBER = os.getenv("POLL_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
polls = {}
votes = {}

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

_start_ttl_cleanup(polls, votes)


def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": POLL_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception:
        pass

@app.route("/polls", methods=["POST"])
def create_poll():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    pid = f"POLL-{int(time.time())}"
    options = data.get("options", [])
    polls[pid] = {"question": data.get("question"), "options": {str(i+1): {"text": opt, "votes": 0} for i, opt in enumerate(options)}, "voters": set(), "status": "active"}
    return jsonify({"poll_id": pid, "instructions": f"Text {', '.join(str(i+1) for i in range(len(options)))} to {POLL_NUMBER}"}), 200

@app.route("/polls/<pid>/broadcast", methods=["POST"])
def broadcast_poll(pid):
    poll = polls.get(pid)
    if not poll: return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    numbers = data.get("numbers", [])
    options_text = chr(10).join(f"  {k}: {v['text']}" for k, v in poll["options"].items())
    msg = f"{poll['question']}\n{options_text}\nReply with your choice number."
    for num in numbers:
        send_sms(num, msg)
    return jsonify({"sent": len(numbers)}), 200

@app.route("/webhooks/messaging", methods=["POST"])
def handle_vote():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    if data.get("event_type") != "message.received" or data.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = data.get("from", {}).get("phone_number", "")
    text = data.get("text", "").strip()
    for pid, poll in polls.items():
        if poll["status"] != "active": continue
        if text in poll["options"]:
            if from_number in poll["voters"]:
                send_sms(from_number, "You already voted! Results will be shared when voting closes.")
            else:
                poll["options"][text]["votes"] += 1
                poll["voters"].add(from_number)
                send_sms(from_number, f"Vote recorded: {poll['options'][text]['text']}. Thanks!")
            return jsonify({"status": "voted"}), 200
    send_sms(from_number, "No active poll found. Check the poll number and try again.")
    return jsonify({"status": "no_poll"}), 200

@app.route("/polls/<pid>/results", methods=["GET"])
def results(pid):
    poll = polls.get(pid)
    if not poll: return jsonify({"error": "Not found"}), 404
    total = sum(v["votes"] for v in poll["options"].values())
    return jsonify({"question": poll["question"], "total_votes": total,
        "results": {k: {"text": v["text"], "votes": v["votes"], "pct": round(v["votes"]/max(total,1)*100, 1)} for k, v in poll["options"].items()}}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "polls": len(polls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
