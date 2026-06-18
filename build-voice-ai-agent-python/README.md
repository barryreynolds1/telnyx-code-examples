# Build a Voice AI Agent with Python

## What Does This Example Do?

Build a complete voice AI agent that answers phone calls, understands natural speech, generates intelligent responses using Telnyx Inference, and speaks them back to the caller — all on a single platform. The agent maintains conversation context across turns, handles silence and errors gracefully, and can transfer callers to a human when requested. This is the end-to-end flow: inbound call → speech recognition → LLM reasoning → text-to-speech response → repeat.

## Who Is This For?

- **AI developers** building voice agents, virtual receptionists, or phone bots.
- **Backend engineers** integrating real-time voice AI into production applications.
- **Startups** replacing IVR trees with conversational AI agents.
- **Enterprise teams** building AI-powered contact center automation.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform — voice, AI inference, speech processing, and telephony run on the same private network. No Frankenstack required.

- **Single platform** — Inference (LLM), telephony (call control), and speech processing (STT/TTS) in one API. No stitching together OpenAI + Twilio + Deepgram + ElevenLabs.
- **Sub-200ms voice AI** — Inference runs co-located with the telephony switch on the Telnyx-owned network. Every vendor boundary adds 30-80ms of latency. Telnyx eliminates the boundaries.
- **Global private network** — Calls traverse Telnyx-owned infrastructure in 60+ countries. Lower latency, higher reliability than the public internet.
- **One bill, one SLA** — When something breaks at 2 AM, one vendor owns the fix. Not five vendors pointing fingers.

## Prerequisites

- Python 3.8 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound voice.
- A Call Control Application configured in the Telnyx Portal with your webhook URL.
- A publicly accessible URL for webhooks (use [ngrok](https://ngrok.com) for local development).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-voice-ai-agent-python
cp .env.example .env
# Edit .env with your Telnyx API key
make setup
make run
```

Then expose your local server:

```bash
ngrok http 5000
```

Copy the ngrok URL and set it as your Call Control Application webhook: `https://your-ngrok-url.ngrok.io/webhooks/voice`

Call your Telnyx number — the AI agent will answer.

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-voice-ai-agent-python
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

### Architecture

```
Caller → Telnyx Phone Number → Call Control Webhook → Your Flask App
                                                          ↓
                                                   Speech-to-Text (gather)
                                                          ↓
                                                   Telnyx Inference API (LLM)
                                                          ↓
                                                   Text-to-Speech (speak)
                                                          ↓
                                                   Caller hears response
```

All of this runs on Telnyx infrastructure. The only external hop is to your webhook server.

### Step 1: Initialize the Telnyx client and inference function

```python
import os
import requests
import telnyx
from flask import Flask, request, jsonify

client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))

def call_telnyx_inference(messages: list) -> str:
    """Send conversation to Telnyx Inference API."""
    response = requests.post(
        "https://api.telnyx.com/v2/ai/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('TELNYX_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": messages,
            "max_tokens": 150,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
```

### Step 2: Handle the call lifecycle

The voice AI agent loop has four stages:

1. **`call.initiated`** — Answer the inbound call
2. **`call.answered`** — Greet the caller with TTS
3. **`call.speak.ended`** — Start listening for speech (gather)
4. **`call.gather.ended`** — Process speech with LLM, respond with TTS, loop back to step 3

```python
@app.route("/webhooks/voice", methods=["POST"])
def handle_voice_webhook():
    payload = request.get_json()
    event_type = payload["data"]["event_type"]
    call_control_id = payload["data"]["call_control_id"]

    if event_type == "call.initiated":
        client.calls.actions.answer(call_control_id)

    elif event_type == "call.answered":
        client.calls.actions.speak(
            call_control_id,
            payload="Hi, thanks for calling. How can I help you?",
            voice="female",
            language_code="en-US",
        )

    elif event_type == "call.speak.ended":
        client.calls.actions.gather(
            call_control_id,
            input_type="speech",
            end_silence_timeout_secs=2,
            timeout_secs=15,
        )

    elif event_type == "call.gather.ended":
        speech = payload["data"]["speech"]["result"]
        ai_response = get_ai_response(call_control_id, speech)
        client.calls.actions.speak(
            call_control_id,
            payload=ai_response,
            voice="female",
            language_code="en-US",
        )

    return jsonify({"status": "ok"}), 200
```

### Step 3: Maintain conversation context

```python
conversations = {}

def get_ai_response(call_control_id: str, user_input: str) -> str:
    if call_control_id not in conversations:
        conversations[call_control_id] = [
            {"role": "system", "content": "You are a helpful voice AI agent..."}
        ]
    conversations[call_control_id].append({"role": "user", "content": user_input})
    ai_response = call_telnyx_inference(conversations[call_control_id])
    conversations[call_control_id].append({"role": "assistant", "content": ai_response})
    return ai_response
```

## Complete Code

See [`app.py`](./app.py) for the full implementation with error handling, transfer logic, conversation management, and health checks.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Agent doesn't answer calls | Call rings but webhook never fires. | Verify your Call Control Application webhook URL in the Telnyx Portal. If using ngrok, confirm the tunnel is active and the URL matches. Check that your phone number is assigned to the Call Control Application. |
| No AI response | Agent answers but goes silent after you speak. | Check that `TELNYX_API_KEY` has inference permissions. Verify the model name in `AI_MODEL` is valid (try `meta-llama/Llama-3.3-70B-Instruct`). Check Flask logs for API errors. |
| Long pauses between turns | Noticeable delay between speaking and hearing a response. | This is normal for the first turn as the model loads. Subsequent turns should be faster. Ensure your webhook server is geographically close to Telnyx infrastructure. Consider using a smaller model for faster responses. |
| Speech not recognized | Agent keeps saying "I didn't catch that." | Check `end_silence_timeout_secs` — increase to 3 if callers speak slowly. Verify `language_code` matches the caller's language. Reduce background noise on test calls. |
| Transfer not working | Caller asks for a human but doesn't get transferred. | Set `TRANSFER_NUMBER` in your `.env` file. The number must be in E.164 format (e.g., `+14155551234`). |

## FAQ

**Q: How much does it cost to run a voice AI agent on Telnyx?**

You pay for three things: the phone call (per-minute voice rate), inference (per-token, varies by model), and the phone number (monthly). There are no per-seat fees, platform fees, or minimums. A typical 3-minute AI call costs under $0.10 total.

**Q: Which AI models can I use?**

Telnyx Inference supports Llama 3.3 70B, Qwen, Kimi K2.5, GPT-5, Claude, and more. See the full list at the [Telnyx AI Models page](https://developers.telnyx.com/docs/inference). You can swap models by changing the `AI_MODEL` environment variable.

**Q: Can I use this for outbound calls too?**

Yes. Replace the `call.initiated` handler with a `client.calls.create()` call to dial out. The rest of the conversation flow is identical.

**Q: How is this different from Vapi or Retell?**

Vapi and Retell are API wrappers that stitch together third-party STT, LLM, and TTS providers behind their API. Every vendor boundary adds 30-80ms of latency and a failure point. Telnyx runs inference, speech processing, and telephony on the same owned infrastructure — fewer hops, lower latency, and one vendor to debug when something breaks.

**Q: Can I use Telnyx AI Assistants instead of raw Call Control?**

Yes. Telnyx AI Assistants provide a no-code/low-code path where you configure the assistant in the Portal and it handles the call flow automatically. This example uses raw Call Control + Inference for full customization. See the [AI Assistants examples](../create-ai-assistant-python/) for the managed approach.

**Q: Do I need a separate STT or TTS provider?**

No. Telnyx Call Control has built-in speech gathering (STT) via `gather` and text-to-speech via `speak`. Both run on Telnyx infrastructure. You can also use the Telnyx AI Assistants for fully managed voice AI with multiple STT/TTS provider options.

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Call Control Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [Telnyx Inference API](https://developers.telnyx.com/docs/inference)
- [AI Assistants](https://developers.telnyx.com/docs/voice/programmable-voice/ai-assistant-start)
- [Python SDK](https://developers.telnyx.com/development/sdk/python)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)
- [Inference Pricing](https://telnyx.com/pricing/inference)

## Related Examples

- [Create an AI Assistant with Python](../create-ai-assistant-python/) — No-code AI agent setup.
- [Route Phone Calls to AI Agent with Python](../route-phone-calls-to-ai-agent-python/) — Simpler webhook-only call routing.
- [Run LLM Inference with Python](../run-llm-inference-python/) — Standalone inference API usage.
- [Record Phone Calls with Python](../record-phone-calls-python/) — Add call recording to your agent.
