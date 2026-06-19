# How to Reduce Latency in PSTN Voice AI Bots

Voice AI latency is the time between when a caller stops speaking and when they hear the AI response. Humans notice delays above 300ms. Most multi-vendor stacks add 500-1500ms. Here is how to get under 200ms with Telnyx.

## Where latency comes from

A typical voice AI stack:

```
Caller speaks
  -> Phone network (PSTN)         ~50ms
  -> Twilio receives audio         ~20ms
  -> Send to Deepgram (STT)        ~80ms  + network hop
  -> STT processing                ~200ms
  -> Send to OpenAI (LLM)          ~60ms  + network hop
  -> LLM processing                ~300ms
  -> Send to ElevenLabs (TTS)      ~80ms  + network hop
  -> TTS processing                ~200ms
  -> Send audio back to Twilio     ~80ms  + network hop
  -> Twilio plays audio            ~20ms
  -> Phone network (PSTN)          ~50ms
                                   --------
                          Total:   ~1,140ms
```

Four vendor boundaries. Four network round trips. Each one adds 60-100ms just for the hop, plus processing time.

## The Telnyx approach

```
Caller speaks
  -> Phone network (PSTN)          ~50ms
  -> Telnyx receives audio          ~5ms   (same network)
  -> Telnyx STT                     ~150ms (co-located)
  -> Telnyx Inference (LLM)         ~200ms (co-located)
  -> Telnyx TTS                     ~50ms  (co-located)
  -> Telnyx plays audio             ~5ms   (same network)
  -> Phone network (PSTN)           ~50ms
                                    --------
                           Total:   ~510ms baseline
                                    ~180ms with streaming
```

One network. Zero vendor hops between stages. Audio stays on the Telnyx backbone from ingestion through response.

## Technique 1: Co-locate everything

Use Telnyx for the full pipeline:

```python
# All three API calls hit the same Telnyx network
TELNYX_API = "https://api.telnyx.com/v2"

# STT: gather speech from the call
requests.post(f"{TELNYX_API}/calls/{call_id}/actions/gather_using_speak", ...)

# LLM: get the AI response (OpenAI-compatible endpoint)
requests.post(f"{TELNYX_API}/ai/chat/completions", ...)

# TTS: speak the response back
requests.post(f"{TELNYX_API}/calls/{call_id}/actions/speak", ...)
```

Same API key, same base URL, same network.

## Technique 2: Stream STT results

Do not wait for the caller to stop speaking before processing. Use partial transcripts:

```python
# Media streaming gives you audio chunks in real time
@app.route("/webhooks/media", methods=["POST"])
def handle_media():
    event = request.get_json()["data"]

    if event["event_type"] == "media.stream.data":
        audio_chunk = event["payload"]["audio"]
        # Send to STT as it arrives, not after silence
        partial_transcript = process_audio(audio_chunk)

        if is_complete_thought(partial_transcript):
            # Start LLM inference before caller fully stops
            response = call_inference(partial_transcript)
```

## Technique 3: Stream TTS output

Do not wait for the full TTS audio to render. Start playing as soon as the first chunk is ready:

```python
# Telnyx TTS can stream audio back while still generating
# The first syllable plays while the rest renders
requests.post(
    f"https://api.telnyx.com/v2/calls/{call_id}/actions/speak",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "payload": ai_response,
        "language": "en-US",
        "voice": "Telnyx.MiMi",
        # Audio starts playing immediately, does not wait for full render
    },
)
```

## Technique 4: Keep LLM responses short

Prompt engineering matters for latency:

```python
SYSTEM_PROMPT = """You are a phone assistant. Rules:
- Respond in 1-2 sentences maximum
- Never use lists or bullet points (this is a phone call)
- If you need more info, ask one specific question
- Do not repeat what the caller said back to them"""
```

A 20-token response renders in ~100ms. A 200-token response takes ~600ms. On a phone call, shorter is always better.

## Technique 5: Use the right model

Smaller models are faster. For phone conversations, you rarely need GPT-4 class reasoning:

| Model | Typical latency | Best for |
|-------|----------------|----------|
| Llama 4 Scout | ~150ms | General phone conversations |
| Kimi K2.5 | ~200ms | Complex reasoning |
| GLM-5.1 | ~120ms | Simple routing and classification |

All available on Telnyx Inference with the same API.

## Measuring latency

Add timing to your webhook handler:

```python
import time

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    event = request.get_json()["data"]

    if event["event_type"] == "call.gather.ended":
        start = time.time()

        transcript = event["payload"].get("speech", {}).get("result", "")
        ai_response = call_inference(transcript)

        inference_ms = (time.time() - start) * 1000
        app.logger.info("Inference latency: %.0fms", inference_ms)

        speak_start = time.time()
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/speak",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"payload": ai_response},
        )
        speak_ms = (time.time() - speak_start) * 1000
        app.logger.info("TTS request latency: %.0fms", speak_ms)
```

## Full source code

- [build-voice-ai-agent-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/build-voice-ai-agent-python) -- Full pipeline with latency logging
- [media-stream-live-transcription-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/media-stream-live-transcription-python) -- Streaming STT
- [ai-live-call-participant-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/ai-live-call-participant-python) -- Real-time AI in live calls

## Resources

- [Telnyx AI Inference docs](https://developers.telnyx.com/docs/ai/inference)
- [Telnyx Media Streaming docs](https://developers.telnyx.com/docs/voice/media-streaming)
- [Telnyx Portal](https://portal.telnyx.com)
