# Run LLM Inference with Node.js

## What Does This Example Do?

Run large language model inference through the Telnyx Inference API using an OpenAI-compatible interface from Node.js. Send chat completion requests, maintain multi-turn conversations, and integrate LLM capabilities into any application. Works as both a CLI tool and an HTTP server.

## Who Is This For?

- AI developers integrating LLM inference into Node.js applications.
- Backend engineers building AI-powered APIs and services.
- Teams evaluating inference providers looking for OpenAI-compatible alternatives.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that runs inference on its own global network.

- OpenAI-compatible API. Same request/response format. Swap your base URL and API key.
- Infrastructure ownership. Inference runs on Telnyx-owned hardware co-located with telephony. Fewer hops, lower latency.
- Multiple models. Llama 3.3 70B, Qwen, Kimi K2.5, and more. Switch models with one parameter.
- Integrated stack. Add voice, SMS, or SIP to your AI app with the same platform and API key.

## Prerequisites

- Node.js 18 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).

## Quick Start



## Implementation Details

### Core inference function



## Complete Code

See [server.js](./server.js) for the full implementation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check TELNYX_API_KEY in .env. Keys start with KEY. |
| Model not available | Try meta-llama/Llama-3.3-70B-Instruct as default. |
| Timeout | Reduce max_tokens or use a smaller model. |

## FAQ

**Q: Is this OpenAI-compatible?**
Yes. Same request/response format. You can use the OpenAI Node.js SDK with the Telnyx base URL.

**Q: Which models are available?**
Llama 3.3 70B, Qwen 3, Kimi K2.5, GPT-5, and more. Check developers.telnyx.com for the current list.

**Q: Can I use this for voice AI?**
Yes. Telnyx inference runs on the same network as telephony for sub-200ms voice AI latency.

## Resources

- [Telnyx Inference Docs](https://developers.telnyx.com/docs/inference)
- [Node.js SDK](https://developers.telnyx.com/development/sdk/node)
- [Inference Pricing](https://telnyx.com/pricing/inference)

## Related Examples

- [Build a Voice AI Agent with Node.js](../build-voice-ai-agent-nodejs/)
- [Create an AI Assistant with Node.js](../create-ai-assistant-nodejs/)
- [Run LLM Inference with Python](../run-llm-inference-python/)
