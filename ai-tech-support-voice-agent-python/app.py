#!/usr/bin/env python3
"""AI Tech Support Voice Agent — IT helpdesk voice agent with knowledge base."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
SUPPORT_NUMBER = os.getenv("SUPPORT_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
active_calls = {}
tickets = []

KB = {"password_reset": "Go to portal.company.com/reset, enter your email, check for the reset link. If not received in 5 minutes, check spam or contact IT directly.",
    "vpn_issues": "Try disconnecting and reconnecting. If that fails, restart the VPN client. For Mac: System Preferences > Network > VPN > disconnect/reconnect. Windows: Settings > Network > VPN.",
    "printer_setup": "Go to Settings > Printers, click Add Printer, select your floor printer. Floor 1: HP-F1-Color, Floor 2: HP-F2-BW, Floor 3: HP-F3-Color.",
    "email_issues": "Clear Outlook cache: File > Account Settings > Data Files > locate .ost file > close Outlook > delete .ost > reopen. For mobile: remove and re-add the account.",
    "wifi_issues": "Forget the network and reconnect. Network: CorpWiFi, use your AD credentials. Guest network: GuestWiFi, password rotates monthly (current on break room whiteboard)."}

SYSTEM_PROMPT = f"You are IT support. Knowledge base: {json.dumps(KB)}. Try to resolve issues using the KB first. If you cannot resolve, create a ticket. Keep responses under 2 sentences."

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
        active_calls[ccid] = {"caller": data.get("from"), "conversation": [{"role": "system", "content": SYSTEM_PROMPT}]}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="IT Support, how can I help you?", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="Could you repeat that?", voice="female", language_code="en-US")
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
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
