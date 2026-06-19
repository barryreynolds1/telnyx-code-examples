# How to Route a Phone Call to an AI Agent with Python

Route live inbound phone calls to an AI voice agent using Telnyx Call Control and AI Inference. The agent answers, listens via STT, thinks via LLM, and speaks back via TTS in real time.

## What you will build

A Flask webhook server that:
1. Receives inbound call events from Telnyx
2. Greets the caller with text-to-speech
3. Listens for speech input
4. Sends the transcript to an LLM for a response
5. Speaks the response back to the caller
6. Loops until the caller hangs up

Total latency: sub-200ms voice-to-voice when using Telnyx Inference, because telephony and AI run on the same private network.

## Prerequisites

- Python 3.8+
- [Telnyx account](https://portal.telnyx.com/sign-up) with API key
- Telnyx phone number with voice enabled
- [Call Control Application](https://portal.telnyx.com/call-control/applications) with webhook URL
- [ngrok](https://ngrok.com) for local development

## Step 1: Set up the project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-voice-ai-agent-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env`:

```
TELNYX_API_KEY=KEY01234...          # portal.telnyx.com/api-keys
TELNYX_NUMBER=+18005551234          # your Telnyx number
CONNECTION_ID=1234567890            # Call Control app ID
AI_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct   # or any model on Telnyx Inference
```

## Step 2: Understand the call flow

```
Caller dials your number
        |
        v
Telnyx receives the call
        |
        v
POST /webhooks/voice  (call.initiated)
  -> Your app answers the call
        |
        v
POST /webhooks/voice  (call.answered)
  -> Your app speaks a greeting via TTS
        |
        v
POST /webhooks/voice  (call.speak.ended)
  -> Your app starts listening (gather)
        |
        v
POST /webhooks/voice  (call.gather.ended)
  -> Transcript received
  -> Send to Telnyx Inference API
  -> Speak the AI response via TTS
  -> Loop back to listening
```

Every state transition is a webhook event. Your app never polls.

## Step 3: The webhook handler

This is the core of the app. Each Telnyx event triggers the next action:

```python
@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    event = request.get_json()["data"]
    event_type = event["event_type"]
    call_id = event["payload"]["call_control_id"]

    if event_type == "call.initiated":
        # Answer the call
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/answer",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json={},
        )

    elif event_type == "call.answered":
        # Greet the caller
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/speak",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json={"payload": "Hello, how can I help you today?", "language": "en-US"},
        )

    elif event_type == "call.speak.ended":
        # Start listening
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/gather_using_speak",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json={
                "payload": "",
                "language": "en-US",
                "voice": "Telnyx.MiMi",
                "minimum_digits": 1,
                "maximum_digits": 0,
            },
        )

    elif event_type == "call.gather.ended":
        # Got the transcript, ask the AI
        transcript = event["payload"].get("speech", {}).get("result", "")
        ai_response = call_inference(transcript)
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/speak",
            headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            json={"payload": ai_response, "language": "en-US"},
        )

    return jsonify({"status": "ok"})
```

## Step 4: AI Inference

Telnyx Inference uses the OpenAI-compatible API format:

```python
def call_inference(user_message):
    response = requests.post(
        "https://api.telnyx.com/v2/ai/chat/completions",
        headers={
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful phone assistant. Keep responses under 2 sentences."},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 150,
        },
    )
    return response.json()["choices"][0]["message"]["content"]
```

This is the same API shape as OpenAI. If you already use the OpenAI Python SDK, change the base URL to `https://api.telnyx.com/v2/ai` and use your Telnyx API key.

## Step 5: Run it

```bash
# Start the server
python app.py

# In another terminal, expose it
ngrok http 5000
```

Copy the ngrok HTTPS URL and set it as the webhook URL in your [Call Control Application](https://portal.telnyx.com/call-control/applications). Call your Telnyx number.

## Why Telnyx for voice AI?

Most voice AI stacks look like this: Twilio for the phone call, Deepgram for STT, OpenAI for the LLM, ElevenLabs for TTS. Four vendors, four network hops, four bills. Every vendor boundary adds 30-80ms of latency.

Telnyx runs the phone call, STT, LLM inference, and TTS on the same private network. One API key. One bill. Sub-200ms round-trip because the audio never leaves the Telnyx network between stages.

## Full source code

See [build-voice-ai-agent-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/build-voice-ai-agent-python) for the complete, production-ready implementation with conversation memory, error handling, and human transfer fallback.

## Related examples

- [route-phone-calls-to-ai-agent](../route-phone-calls-to-ai-agent-python/) -- Route to managed AI Assistant
- [ai-live-call-participant](../ai-live-call-participant-python/) -- AI joins a live multi-party call
- [ai-sales-coach-whisper](../ai-sales-coach-whisper-python/) -- Live coaching whispered to reps
- [full-stack-ai-contact-center](../full-stack-ai-contact-center-python/) -- Complete contact center

## Resources

- [Telnyx Call Control docs](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx AI Inference docs](https://developers.telnyx.com/docs/ai/inference)
- [Telnyx Portal](https://portal.telnyx.com)
