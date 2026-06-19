# Build a Voice AI Agent with Node.js

## What Does This Example Do?

Build a complete voice AI agent that answers phone calls, understands natural speech, generates intelligent responses using Telnyx Inference, and speaks them back to the caller. The agent maintains conversation context, handles silence gracefully, and can transfer callers to a human. All on a single platform.

## Who Is This For?

- AI developers building voice agents, virtual receptionists, or phone bots.
- Backend engineers integrating real-time voice AI into production applications.
- Startups replacing IVR trees with conversational AI agents.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform. Voice, AI inference, speech processing, and telephony run on the same private network. No Frankenstack.

- Single platform: Inference (LLM), telephony (call control), and speech processing (STT/TTS) in one API.
- Sub-200ms voice AI: Inference co-located with the telephony switch. Every vendor boundary adds 30-80ms. Telnyx eliminates the boundaries.
- Global private network: Calls traverse Telnyx-owned infrastructure in 60+ countries.
- One bill, one SLA: When something breaks, one vendor owns the fix.

## Prerequisites

- Node.js 18 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound voice.
- A Call Control Application configured with your webhook URL.
- A publicly accessible URL for webhooks (use [ngrok](https://ngrok.com) for local development).

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-voice-ai-agent-nodejs
cp .env.example .env
# Edit .env with your Telnyx API key
npm install
node server.js
```

Expose with ngrok:

```bash
ngrok http 5000
```

Set the ngrok URL as your webhook, then call your Telnyx number.

## Implementation Details

### Architecture

```
Caller -> Telnyx Phone Number -> Call Control Webhook -> Your Express App
                                                            |
                                                    Speech-to-Text (gather)
                                                            |
                                                    Telnyx Inference API (LLM)
                                                            |
                                                    Text-to-Speech (speak)
                                                            |
                                                    Caller hears response
```

### Call lifecycle

1. `call.initiated` - Answer the inbound call
2. `call.answered` - Greet the caller with TTS
3. `call.speak.ended` - Start listening for speech (gather)
4. `call.gather.ended` - Process speech with LLM, respond with TTS, loop back to step 3

## Complete Code

See [server.js](./server.js) for the full implementation with error handling, conversation management, and health checks.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent does not answer | Verify webhook URL in Telnyx Portal. Check ngrok is active. |
| No AI response | Check TELNYX_API_KEY has inference permissions. Verify model name. |
| Long pauses | Normal on first turn. Ensure webhook server is near Telnyx infrastructure. |
| Speech not recognized | Increase end_silence_timeout_secs. Check language_code. |

## FAQ

**Q: How much does it cost?**
You pay for the call (per-minute), inference (per-token), and phone number (monthly). No per-seat fees or minimums. A typical 3-minute AI call costs under $0.10 total.

**Q: Which AI models can I use?**
Llama 3.3 70B, Qwen, Kimi K2.5, GPT-5, and more. Change the AI_MODEL environment variable.

**Q: How is this different from Vapi or Retell?**
Vapi and Retell stitch together third-party STT, LLM, and TTS providers. Every vendor boundary adds 30-80ms of latency. Telnyx runs inference, speech processing, and telephony on the same owned infrastructure.

**Q: Can I use Telnyx AI Assistants instead?**
Yes. AI Assistants provide a managed path where you configure the agent in the Portal. This example uses raw Call Control + Inference for full customization.

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Call Control Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [Telnyx Inference API](https://developers.telnyx.com/docs/inference)
- [Node.js SDK](https://developers.telnyx.com/development/sdk/node)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [Route Phone Calls to AI Agent with Node.js](../route-phone-calls-to-ai-agent-nodejs/)
- [Run LLM Inference with Node.js](../run-llm-inference-nodejs/)
- [Create an AI Assistant with Node.js](../create-ai-assistant-nodejs/)
- [Build a Voice AI Agent with Python](../build-voice-ai-agent-python/)
