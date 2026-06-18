#!/usr/bin/env python3
"""AI Voice Agent with Function Calling — voice agent that calls external APIs mid-conversation."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
AGENT_NUMBER = os.getenv("AGENT_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
active_calls = {}

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

_start_ttl_cleanup(active_calls)


TOOLS = [
    {"type": "function", "function": {"name": "check_weather", "description": "Get current weather for a city", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "lookup_order", "description": "Look up order status by order number", "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "check_account_balance", "description": "Check account balance by account number", "parameters": {"type": "object", "properties": {"account_id": {"type": "string"}}, "required": ["account_id"]}}},
]

def execute_function(name, args):
    if name == "check_weather":
        return json.dumps({"city": args.get("city"), "temp": "72F", "condition": "Partly cloudy", "humidity": "45%"})
    elif name == "lookup_order":
        return json.dumps({"order_id": args.get("order_id"), "status": "shipped", "eta": "June 20", "carrier": "FedEx"})
    elif name == "check_account_balance":
        return json.dumps({"account_id": args.get("account_id"), "balance": "$1,234.56", "due_date": "July 1"})
    return json.dumps({"error": "Unknown function"})

def call_inference(messages, max_tokens=200):
    payload = {"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.5, "tools": TOOLS}
    try:
        resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=20)
    except Exception as e:
        app.logger.error("Request failed: %s", e)
    resp.raise_for_status()
    choice = resp.json()["choices"][0]
    msg = choice["message"]
    if msg.get("tool_calls"):
        for tc in msg["tool_calls"]:
            fn = tc["function"]
            result = execute_function(fn["name"], json.loads(fn.get("arguments", "{}")))
            messages.append(msg)
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
        return call_inference(messages, max_tokens)
    return msg["content"]

SYSTEM_PROMPT = "You are a helpful voice assistant with access to real-time tools. You can check weather, look up orders, and check account balances. Use tools when the user asks. Keep voice responses under 2 sentences."

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    call = active_calls.get(ccid)
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        active_calls[ccid] = {"caller": data.get("from"), "conversation": [{"role": "system", "content": SYSTEM_PROMPT}]}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="Hi! I can check weather, look up orders, or check your account balance. What do you need?", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="I didn't catch that. What can I help with?", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": speech})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        active_calls.pop(ccid, None)
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active": len(active_calls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
