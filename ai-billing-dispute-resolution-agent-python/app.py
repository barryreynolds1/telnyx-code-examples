#!/usr/bin/env python3
"""AI Billing Dispute Resolution Agent — handles billing questions with account lookup."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
BILLING_NUMBER = os.getenv("BILLING_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
active_calls = {}
disputes = []

ACCOUNTS = {"1001": {"name": "Jane Smith", "balance": 234.56, "last_payment": "2026-06-01", "plan": "Pro", "charges": [{"desc": "Monthly subscription", "amount": 99.00}, {"desc": "Overage - API calls", "amount": 45.50}, {"desc": "Support add-on", "amount": 29.99}]},
    "1002": {"name": "Bob Corp", "balance": 0, "last_payment": "2026-06-10", "plan": "Enterprise", "charges": [{"desc": "Annual plan", "amount": 499.00}]}}

SYSTEM_PROMPT = """You are a billing support specialist. You can look up accounts by number and explain charges. For disputes:
1. Verify the customer's identity (account number)
2. Review the charge in question
3. If the charge is correct, explain why clearly
4. If there's a legitimate dispute, offer a credit or escalate
Be empathetic and solution-oriented. Keep responses under 2 sentences."""

def call_inference(messages, max_tokens=150):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.4}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    call = active_calls.get(ccid)
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        active_calls[ccid] = {"caller": data.get("from"), "conversation": [{"role": "system", "content": SYSTEM_PROMPT + " Available accounts: " + json.dumps(ACCOUNTS)}], "account": None}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="Hi, you've reached billing support. Can I get your account number to pull up your information?", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="dtmf speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        digits = data.get("digits", "")
        input_text = digits or speech
        if not input_text:
            client.calls.actions.speak(ccid, payload="Could you repeat that?", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": input_text})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if call and len(call["conversation"]) > 4:
            disputes.append({"caller": call["caller"], "exchanges": len(call["conversation"]) // 2, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/disputes", methods=["GET"])
def list_disputes():
    return jsonify({"disputes": disputes[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "active": len(active_calls), "disputes": len(disputes)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
