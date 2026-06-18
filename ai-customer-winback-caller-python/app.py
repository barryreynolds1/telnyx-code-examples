#!/usr/bin/env python3
"""AI Customer Winback Caller — AI calls churned customers with personalized re-engagement offers."""
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
WINBACK_NUMBER = os.getenv("WINBACK_NUMBER")
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

winback_results = []

def call_inference(messages, max_tokens=150):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/winback", methods=["POST"])
def start_winback():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    customer = data
    prompt = f"You are calling {customer.get('name', 'a former customer')} who cancelled {customer.get('months_ago', 'recently')}. Their reason was: {customer.get('cancel_reason', 'unknown')}. Offer: {customer.get('offer', '20% off for 3 months')}. Be warm, not pushy. If they say no, thank them and end gracefully. Under 2 sentences per response."
    try:
        resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"to": customer.get("phone", timeout=10), "from": WINBACK_NUMBER, "connection_id": CONNECTION_ID}, timeout=10)
        ccid = resp.json().get("data", {}).get("call_control_id")
        if ccid:
            active_calls[ccid] = {"customer": customer, "conversation": [{"role": "system", "content": prompt}], "start": time.time()}
        return jsonify({"status": "calling"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    call = active_calls.get(ccid)
    if event_type == "call.answered" and call:
        name = call["customer"].get("name", "there")
        greeting = f"Hi {name}! This is calling from the team. We noticed you left us a while back and we miss having you. Do you have a quick minute?"
        client.calls.actions.speak(ccid, payload=greeting, voice="female", language_code="en-US")
        call["conversation"].append({"role": "assistant", "content": greeting})
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="Sorry, I didn't catch that. Are you interested in coming back?", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": speech})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if call:
            winback_results.append({"customer": call["customer"].get("name"), "duration": int(time.time() - call["start"]),
                "exchanges": len([m for m in call["conversation"] if m["role"] == "user"])})
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/results", methods=["GET"])
def get_results():
    return jsonify({"results": winback_results[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active": len(active_calls), "completed": len(winback_results)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
