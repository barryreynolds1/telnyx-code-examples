#!/usr/bin/env python3
"""Full-Stack AI Contact Center — complete contact center: IVR + queue + AI agent assist + recording + live analytics."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
MAIN_NUMBER = os.getenv("MAIN_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
API = "https://api.telnyx.com/v2"
INFERENCE_URL = f"{API}/ai/chat/completions"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}

queues = {"sales": {"agents": [], "waiting": [], "name": "Sales"},
    "support": {"agents": [], "waiting": [], "name": "Support"},
    "billing": {"agents": [], "waiting": [], "name": "Billing"}}
active_calls = {}
call_stats = {"total": 0, "answered": 0, "abandoned": 0, "avg_wait": 0, "wait_times": []}
recordings = []

def call_inference(messages, max_tokens=200):
    resp = requests.post(INFERENCE_URL, headers=headers,
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.3}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/agents", methods=["POST"])
def register_agent():
    data = request.get_json()
    agent = {"id": data.get("id", f"AGT-{int(time.time())}"), "name": data.get("name"),
        "queue": data.get("queue", "support"), "status": "available", "calls_handled": 0}
    queue = queues.get(agent["queue"])
    if queue:
        queue["agents"].append(agent)
    return jsonify({"agent": agent}), 200

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        call_stats["total"] += 1
        active_calls[ccid] = {"caller": data.get("from"), "start": time.time(), "queue": None, "status": "ivr"}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid,
            payload="Welcome to Acme Corp. Press 1 for Sales, 2 for Support, 3 for Billing.",
            voice="female", language_code="en-US")
        return jsonify({"status": "ivr"}), 200
    elif event_type == "call.speak.ended":
        call = active_calls.get(ccid, {})
        if call.get("status") == "ivr":
            client.calls.actions.gather(ccid, input_type="dtmf", timeout_secs=10, min_digits=1, max_digits=1)
        elif call.get("status") == "ai_assist":
            client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=20, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended":
        call = active_calls.get(ccid, {})
        if call.get("status") == "ivr":
            digits = data.get("digits", "")
            queue_map = {"1": "sales", "2": "support", "3": "billing"}
            queue_name = queue_map.get(digits, "support")
            call["queue"] = queue_name
            call["status"] = "ai_assist"
            queue = queues.get(queue_name, {})
            available = [a for a in queue.get("agents", []) if a["status"] == "available"]
            if available:
                agent = available[0]
                agent["status"] = "busy"
                call["status"] = "connected"
                call_stats["answered"] += 1
                wait = time.time() - call["start"]
                call_stats["wait_times"].append(wait)
                client.calls.actions.speak(ccid, payload=f"Connecting you to {agent['name']} in {queue.get('name', queue_name)}.",
                    voice="female", language_code="en-US")
            else:
                client.calls.actions.speak(ccid,
                    payload=f"All {queue.get('name', queue_name)} agents are busy. Our AI assistant can help while you wait. What do you need?",
                    voice="female", language_code="en-US")
        elif call.get("status") == "ai_assist":
            speech = data.get("speech", {}).get("result", "")
            if speech:
                try:
                    response = call_inference([
                        {"role": "system", "content": f"You are a {call.get('queue', 'support')} assistant for Acme Corp. Help the caller. Keep responses under 2 sentences. If you cannot resolve, say you will transfer to a human agent."},
                        {"role": "user", "content": speech}])
                    client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
                except Exception:
                    client.calls.actions.speak(ccid, payload="Let me transfer you to an agent.",
                        voice="female", language_code="en-US")
        return jsonify({"status": "processed"}), 200
    elif event_type == "call.recording.saved":
        recordings.append({"call_id": ccid, "url": data.get("recording_urls", {}).get("mp3"),
            "duration": data.get("duration_secs"), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "recorded"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if call and call.get("status") != "connected":
            call_stats["abandoned"] += 1
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/dashboard", methods=["GET"])
def dashboard():
    wait_times = call_stats["wait_times"]
    avg_wait = sum(wait_times) / max(len(wait_times), 1)
    queue_status = {}
    for qname, q in queues.items():
        available = sum(1 for a in q["agents"] if a["status"] == "available")
        queue_status[qname] = {"agents": len(q["agents"]), "available": available, "waiting": len(q["waiting"])}
    return jsonify({"total_calls": call_stats["total"], "answered": call_stats["answered"],
        "abandoned": call_stats["abandoned"], "avg_wait_secs": round(avg_wait, 1),
        "active_calls": len(active_calls), "queues": queue_status,
        "recordings": len(recordings)}), 200

@app.route("/queues", methods=["GET"])
def list_queues():
    return jsonify({"queues": {k: {"name": v["name"], "agents": len(v["agents"]), "waiting": len(v["waiting"])} for k, v in queues.items()}}), 200

@app.route("/recordings", methods=["GET"])
def list_recordings():
    return jsonify({"recordings": recordings[-20:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active_calls": len(active_calls), "total_calls": call_stats["total"]}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
