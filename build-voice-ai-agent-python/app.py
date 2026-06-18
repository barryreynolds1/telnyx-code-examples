#!/usr/bin/env python3
"""Build a complete voice AI agent with Telnyx — inbound call handling, AI conversation, and call control."""

import os
import json
import requests
import telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time

load_dotenv()

app = Flask(__name__)

# Initialize Telnyx client
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")

# Configuration
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", (
    "You are a helpful voice AI agent for a business. "
    "Keep responses concise — under 2 sentences — since this is a phone call. "
    "Be natural and conversational. If the caller wants to speak with a human, "
    "say you will transfer them now."
))
TRANSFER_NUMBER = os.getenv("TRANSFER_NUMBER", "")

# In-memory conversation store (use Redis/database in production)
conversations = {}

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

_start_ttl_cleanup(conversations)



def call_telnyx_inference(messages: list) -> str:
    """Send conversation to Telnyx Inference API and return the response."""
    response = requests.post(
        "https://api.telnyx.com/v2/ai/chat/completions",
        headers={
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": AI_MODEL,
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7,
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def get_ai_response(call_control_id: str, user_input: str) -> str:
    """Get AI response for a caller, maintaining conversation history."""
    if call_control_id not in conversations:
        conversations[call_control_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    conversations[call_control_id].append({"role": "user", "content": user_input})

    ai_response = call_telnyx_inference(conversations[call_control_id])

    conversations[call_control_id].append({"role": "assistant", "content": ai_response})

    # Keep conversation history manageable (last 20 messages + system prompt)
    if len(conversations[call_control_id]) > 21:
        conversations[call_control_id] = (
            conversations[call_control_id][:1]
            + conversations[call_control_id][-20:]
        )

    return ai_response


@app.route("/webhooks/voice", methods=["POST"])
def handle_voice_webhook():
    """Handle all voice webhook events from Telnyx."""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No payload"}), 400

        event_type = payload.get("data", {}).get("event_type")
        call_control_id = payload.get("data", {}).get("call_control_id")

        if not event_type or not call_control_id:
            return jsonify({"error": "Missing event data"}), 400

        # --- Inbound call received ---
        if event_type == "call.initiated":
            direction = payload["data"].get("direction")
            if direction == "incoming":
                client.calls.actions.answer(call_control_id)
            return jsonify({"status": "answering"}), 200

        # --- Call answered — greet and start gathering speech ---
        elif event_type == "call.answered":
            client.calls.actions.speak(
                call_control_id,
                payload="Hi, thanks for calling. How can I help you today?",
                voice="female",
                language_code="en-US",
            )
            return jsonify({"status": "greeting"}), 200

        # --- Greeting finished — start listening ---
        elif event_type == "call.speak.ended":
            client.calls.actions.gather(
                call_control_id,
                input_type="speech",
                end_silence_timeout_secs=2,
                timeout_secs=15,
                language_code="en-US",
            )
            return jsonify({"status": "listening"}), 200

        # --- Speech gathered — process with AI ---
        elif event_type == "call.gather.ended":
            speech_result = payload["data"].get("speech", {}).get("result", "")

            if not speech_result:
                # No speech detected — prompt again
                client.calls.actions.speak(
                    call_control_id,
                    payload="I didn't catch that. Could you repeat?",
                    voice="female",
                    language_code="en-US",
                )
                return jsonify({"status": "reprompting"}), 200

            # Get AI response
            ai_response = get_ai_response(call_control_id, speech_result)

            # Check if caller wants a transfer
            transfer_phrases = ["transfer", "speak with a human", "talk to someone", "real person"]
            if any(phrase in speech_result.lower() for phrase in transfer_phrases) and TRANSFER_NUMBER:
                client.calls.actions.speak(
                    call_control_id,
                    payload="Transferring you now. One moment please.",
                    voice="female",
                    language_code="en-US",
                )
                # Transfer happens after speak ends (see call.speak.ended with transfer logic)
                conversations[call_control_id] = conversations.get(call_control_id, [])
                conversations[call_control_id].append({"_transfer": True})
                return jsonify({"status": "transferring"}), 200

            # Speak the AI response back to the caller
            client.calls.actions.speak(
                call_control_id,
                payload=ai_response,
                voice="female",
                language_code="en-US",
            )
            return jsonify({"status": "responding", "response": ai_response}), 200

        # --- Call ended — clean up ---
        elif event_type == "call.hangup":
            conversations.pop(call_control_id, None)
            return jsonify({"status": "call_ended"}), 200

        return jsonify({"status": "event_received", "event_type": event_type}), 200

    except telnyx.AuthenticationError:
        return jsonify({"error": "Invalid API key"}), 401
    except telnyx.RateLimitError:
        return jsonify({"error": "Rate limit exceeded"}), 429
    except telnyx.APIStatusError as e:
        return jsonify({"error": "API error", "status_code": e.status_code}), e.status_code
    except telnyx.APIConnectionError:
        return jsonify({"error": "Network error"}), 503
    except Exception as e:
        app.logger.error("Webhook error: %s", e)
        return jsonify({"error": "Internal error"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "active_calls": len(conversations)}), 200


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 5000)),
    )
