#!/usr/bin/env python3
"""Omnichannel AI Receptionist — one AI brain across voice, SMS, and WhatsApp."""

import os
import json
import requests
import telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time

load_dotenv()

app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
BUSINESS_NUMBER = os.getenv("BUSINESS_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"

# Shared context store: customer_number -> conversation history across all channels
customer_context = {}

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

_start_ttl_cleanup(customer_context)


SYSTEM_PROMPT = """You are a friendly AI receptionist for a business. You handle calls, texts, and WhatsApp messages.
You can: answer FAQs, book appointments, provide business hours, give directions, transfer to a human.
Keep voice responses under 2 sentences. Text/WhatsApp responses can be slightly longer.
Always remember previous interactions — if a customer called yesterday, reference it.
Business hours: Monday-Friday 9am-6pm, Saturday 10am-2pm, closed Sunday."""


def get_customer_history(customer_number, channel):
    """Get or create conversation history for a customer across channels."""
    if customer_number not in customer_context:
        customer_context[customer_number] = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
            "channels_used": set(),
            "interaction_count": 0,
        }
    ctx = customer_context[customer_number]
    ctx["channels_used"].add(channel)
    ctx["interaction_count"] += 1
    return ctx


def call_inference(messages, max_tokens=200):
    """Call Telnyx Inference API."""
    resp = requests.post(
        INFERENCE_URL,
        headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def send_message(to, text, media_url=None):
    """Send SMS or MMS via Telnyx."""
    payload = {"from": BUSINESS_NUMBER, "to": to, "text": text}
    if MESSAGING_PROFILE_ID:
        payload["messaging_profile_id"] = MESSAGING_PROFILE_ID
    if media_url:
        payload["media_urls"] = [media_url]
    try:
        requests.post(
            "https://api.telnyx.com/v2/messages",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
    except requests.RequestException as e:
        app.logger.error("Send message failed: %s", e)


# ─── Voice Webhook ───
@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    """Handle inbound voice calls."""
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No payload"}), 400

    data = payload.get("data", {})
    p = data.get("payload", {})
    event_type = data.get("event_type")
    call_control_id = p.get("call_control_id")

    if event_type == "call.initiated" and p.get("direction") == "incoming":
        customer = p.get("from", "unknown")
        ctx = get_customer_history(customer, "voice")
        # Add channel context for the AI
        if "sms" in ctx["channels_used"] or "whatsapp" in ctx["channels_used"]:
            ctx["messages"].append({
                "role": "system",
                "content": f"This customer previously contacted us via {', '.join(ctx['channels_used'] - {'voice'})}. Reference prior conversation if relevant.",
            })
        client.calls.actions.answer(call_control_id)
        return jsonify({"status": "answering"}), 200

    elif event_type == "call.answered":
        customer = p.get("from", "unknown")
        ctx = get_customer_history(customer, "voice")
        greeting = "Welcome back! How can I help you today?" if ctx["interaction_count"] > 1 else "Hi, thanks for calling! How can I help you today?"
        client.calls.actions.speak(call_control_id, payload=greeting, voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200

    elif event_type == "call.speak.ended":
        client.calls.actions.gather(call_control_id, input_type="speech", end_silence_timeout_secs=2, timeout_secs=15, language_code="en-US")
        return jsonify({"status": "listening"}), 200

    elif event_type == "call.gather.ended":
        speech = p.get("speech", {}).get("result", "")
        customer = p.get("from", "unknown")
        if not speech:
            client.calls.actions.speak(call_control_id, payload="Sorry, I didn't catch that.", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200

        ctx = get_customer_history(customer, "voice")
        ctx["messages"].append({"role": "user", "content": f"[voice call] {speech}"})
        response = call_inference(ctx["messages"], max_tokens=100)
        ctx["messages"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(call_control_id, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200

    elif event_type == "call.hangup":
        return jsonify({"status": "call_ended"}), 200

    return jsonify({"status": "event_received"}), 200


# ─── Messaging Webhook (SMS + WhatsApp) ───
@app.route("/webhooks/messaging", methods=["POST"])
def handle_messaging():
    """Handle inbound SMS and WhatsApp messages with shared context."""
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No payload"}), 400

    data = payload.get("data", {})
    p = data.get("payload", {})
    event_type = data.get("event_type")

    if event_type != "message.received":
        return jsonify({"status": "ignored"}), 200

    direction = p.get("direction")
    if direction != "inbound":
        return jsonify({"status": "ignored"}), 200

    from_number = p.get("from", {}).get("phone_number", "")
    text = p.get("text", "")
    channel = "whatsapp" if p.get("messaging_profile_id") and "whatsapp" in str(p.get("from", {}).get("carrier", "")).lower() else "sms"

    if not from_number or not text:
        return jsonify({"status": "ignored"}), 200

    ctx = get_customer_history(from_number, channel)
    ctx["messages"].append({"role": "user", "content": f"[{channel}] {text}"})

    response = call_inference(ctx["messages"], max_tokens=300)
    ctx["messages"].append({"role": "assistant", "content": response})

    send_message(from_number, response)

    return jsonify({"status": "responded", "channel": channel}), 200


@app.route("/customers", methods=["GET"])
def list_customers():
    """List all customers and their interaction history across channels."""
    customers = {}
    for number, ctx in customer_context.items():
        customers[number] = {
            "channels": list(ctx["channels_used"]),
            "interactions": ctx["interaction_count"],
            "message_count": len([m for m in ctx["messages"] if m["role"] == "user"]),
        }
    return jsonify(customers), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "customers_tracked": len(customer_context)}), 200


if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 5000)))
