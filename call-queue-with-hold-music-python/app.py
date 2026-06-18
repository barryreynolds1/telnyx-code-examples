#!/usr/bin/env python3
"""Call Queue with Hold Music — queue callers with position announcements and hold music, route to agents."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
QUEUE_NUMBER = os.getenv("QUEUE_NUMBER")
AGENT_NUMBERS = os.getenv("AGENT_NUMBERS", "").split(",")
CONNECTION_ID = os.getenv("CONNECTION_ID")
caller_queue = []
active_calls = {}
agents = {num.strip(): {"status": "available", "calls_handled": 0} for num in AGENT_NUMBERS if num.strip()}

def get_available_agent():
    for num, agent in agents.items():
        if agent["status"] == "available":
            return num
    return None

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        active_calls[ccid] = {"caller": data.get("from"), "state": "queued", "queued_at": time.time()}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        agent_num = get_available_agent()
        if agent_num:
            agents[agent_num]["status"] = "busy"
            active_calls[ccid]["state"] = "connecting"
            client.calls.actions.speak(ccid, payload="Thank you for calling. Connecting you now.", voice="female", language_code="en-US")
        else:
            position = len([c for c in active_calls.values() if c.get("state") == "queued"]) 
            caller_queue.append(ccid)
            client.calls.actions.speak(ccid, payload=f"All agents are busy. You are number {position} in the queue. Please hold.", voice="female", language_code="en-US")
            active_calls[ccid]["state"] = "holding"
        return jsonify({"status": "routing"}), 200
    elif event_type == "call.speak.ended":
        call = active_calls.get(ccid)
        if call and call.get("state") == "holding":
            client.calls.actions.playback_start(ccid, audio_url="https://file-examples.com/storage/fedc3e8bdb6832b296ac7cc/2017/11/file_example_MP3_700KB.mp3", loop="infinity")
        elif call and call.get("state") == "connecting":
            agent_num = get_available_agent() or (AGENT_NUMBERS[0] if AGENT_NUMBERS else "")
            if agent_num:
                client.calls.actions.transfer(ccid, to=agent_num)
        return jsonify({"status": "ok"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if ccid in caller_queue:
            caller_queue.remove(ccid)
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/queue", methods=["GET"])
def queue_status():
    return jsonify({"queue_length": len(caller_queue), "agents": agents}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "queue": len(caller_queue), "active": len(active_calls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
