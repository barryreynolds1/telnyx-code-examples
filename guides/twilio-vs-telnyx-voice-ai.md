# Telnyx vs Twilio for Voice AI

A technical comparison for developers building voice AI agents over PSTN.

## Architecture difference

**Twilio approach** (multi-vendor):
```
Twilio (telephony) -> Deepgram (STT) -> OpenAI (LLM) -> ElevenLabs (TTS) -> Twilio (playback)
     4 vendors, 4 network hops, 4 bills
```

**Telnyx approach** (single platform):
```
Telnyx (telephony + STT + LLM + TTS + playback)
     1 vendor, 0 network hops between stages, 1 bill
```

## Feature comparison

| Capability | Telnyx | Twilio |
|-----------|--------|--------|
| **Programmable voice** | Call Control API with webhooks | TwiML + REST API |
| **SIP trunking** | Elastic (no channel limits) | Elastic SIP |
| **AI inference (LLM)** | Built-in, OpenAI-compatible API | Not offered (use third party) |
| **Text-to-speech** | Built-in, multiple voices | Built-in (limited voices) |
| **Speech-to-text** | Built-in via gather/media stream | Built-in via gather |
| **Media streaming** | WebSocket, real-time audio | Media Streams (WebSocket) |
| **Conference / whisper** | Native conference API | Conference API |
| **Call recording** | Built-in with storage | Built-in |
| **WebRTC** | Supported | Supported |
| **Network ownership** | Owns IP backbone in 60+ countries | Resells carrier capacity |
| **AI model choice** | Llama, Kimi, GLM, Mistral, etc. | N/A (bring your own) |

## Latency

The critical difference for voice AI is inter-stage latency.

With Twilio, each vendor hop adds 60-100ms of network transit:

| Stage | Twilio stack | Telnyx stack |
|-------|-------------|-------------|
| PSTN to platform | ~50ms | ~50ms |
| Platform to STT | ~80ms (external) | ~5ms (co-located) |
| STT processing | ~200ms | ~150ms |
| STT to LLM | ~60ms (external) | ~0ms (same network) |
| LLM processing | ~300ms | ~200ms |
| LLM to TTS | ~80ms (external) | ~0ms (same network) |
| TTS processing | ~200ms | ~50ms |
| TTS to playback | ~80ms (external) | ~5ms (same network) |
| **Total** | **~1,050ms** | **~460ms** |

With streaming optimizations on Telnyx, effective latency drops below 200ms.

## Pricing model

| Item | Telnyx | Twilio |
|------|--------|--------|
| Voice (inbound, per min) | From $0.0035 | From $0.0085 |
| Voice (outbound, per min) | From $0.005 | From $0.013 |
| AI inference | Included (per token) | N/A (pay OpenAI separately) |
| TTS | Included | Included (basic voices) |
| Phone numbers | From $1/mo | From $1.15/mo |
| SIP trunking | Per minute, no channel fees | Per minute |

Twilio users building voice AI also pay separately for Deepgram/AssemblyAI (STT), OpenAI/Anthropic (LLM), and ElevenLabs/PlayHT (TTS). Telnyx bundles all of these.

## Code comparison

**Twilio** -- answer a call and speak:
```python
from twilio.twiml.voice_response import VoiceResponse

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    resp.say("Hello from Twilio")
    return str(resp)
```

**Telnyx** -- answer a call and speak:
```python
@app.route("/webhooks/voice", methods=["POST"])
def voice():
    event = request.get_json()["data"]
    call_id = event["payload"]["call_control_id"]

    if event["event_type"] == "call.initiated":
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/answer",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={},
        )
    elif event["event_type"] == "call.answered":
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/speak",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"payload": "Hello from Telnyx", "language": "en-US"},
        )
    return jsonify({"status": "ok"})
```

Telnyx uses webhooks for every state transition. More verbose, but you get full control over the call flow -- including mid-call AI, transfers, conferencing, and recording without changing the programming model.

## Migration

Use [migrate-from-twilio-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/migrate-from-twilio-python) to audit your Twilio account and provision equivalent resources on Telnyx automatically.

## When to choose Telnyx

- You are building voice AI and need low latency
- You want telephony + AI inference + TTS on one platform
- You need SIP trunking with no channel limits
- You want to avoid managing 4+ vendor integrations
- You need a global network you do not share with other tenants

## When to choose Twilio

- You have a large existing Twilio codebase and do not need AI features
- You need Twilio-specific integrations (Flex, Studio)
- Your team is already trained on TwiML

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Migration guide](https://github.com/team-telnyx/telnyx-code-examples/tree/main/migrate-from-twilio-python)
- [Build a voice AI agent](https://github.com/team-telnyx/telnyx-code-examples/tree/main/build-voice-ai-agent-python)
