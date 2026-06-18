# Run LLM Inference with Python

## What Does This Example Do?

Run large language model inference through the Telnyx Inference API using an OpenAI-compatible interface. Send chat completion requests, maintain multi-turn conversations, and integrate LLM capabilities into any Python application. Works as both a CLI tool for quick testing and an HTTP server for production use.

## Who Is This For?

- **AI developers** integrating LLM inference into applications.
- **Backend engineers** building AI-powered features — chatbots, summarization, classification, code generation.
- **Teams evaluating inference providers** looking for OpenAI-compatible alternatives with infrastructure ownership.
- **Voice AI builders** who need the inference component before wiring it to telephony.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that runs inference on its own global network — not rented GPU clouds.

- **OpenAI-compatible API** — Same request/response format. Swap your base URL and API key. No code changes.
- **Infrastructure ownership** — Inference runs on Telnyx-owned hardware co-located with the telephony network. Fewer hops, lower latency, no middlemen.
- **Multiple models** — Llama 3.3 70B, Qwen, Kimi K2.5, and more. Switch models with one parameter.
- **Integrated stack** — When you're ready to add voice, SMS, or SIP to your AI app, it is the same platform and API key. No Frankenstack.

## Prerequisites

- Python 3.8 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- pip (Python package manager).

## Quick Start

### Option 1: CLI (fastest)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/run-llm-inference-python
cp .env.example .env
# Edit .env with your Telnyx API key
make setup
python app.py "What is SIP trunking and when would I use it?"
```

### Option 2: HTTP Server

```bash
make setup
make run
# In another terminal:
curl -X POST http://localhost:5000/inference/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is SIP trunking?"}'
```

### Option 3: Docker

```bash
cp .env.example .env
make docker-build
make docker-run
```

## Implementation Details

### The core: one function, one API call

```python
import requests

def chat_completion(messages, model="meta-llama/Llama-3.3-70B-Instruct"):
    response = requests.post(
        "https://api.telnyx.com/v2/ai/chat/completions",
        headers={
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "max_tokens": 500,
        },
    )
    response.raise_for_status()
    return response.json()
```

If you have used the OpenAI SDK, this is the same format. Different base URL, Telnyx API key instead of OpenAI key.

### Multi-turn conversations

```python
messages = [
    {"role": "system", "content": "You are a telecom infrastructure expert."},
    {"role": "user", "content": "What is STIR/SHAKEN?"},
]
result = chat_completion(messages)
print(result["choices"][0]["message"]["content"])

# Continue the conversation
messages.append(result["choices"][0]["message"])
messages.append({"role": "user", "content": "How does it prevent spam calls?"})
result = chat_completion(messages)
```

### Using with OpenAI SDK (drop-in replacement)

```python
from openai import OpenAI

client = OpenAI(
    api_key=TELNYX_API_KEY,
    base_url="https://api.telnyx.com/v2/ai",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## Complete Code

See [`app.py`](./app.py) for the full implementation with HTTP server, CLI mode, error handling, and health checks.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| 401 Unauthorized | Invalid or missing API key. | Verify TELNYX_API_KEY in .env matches your key from portal.telnyx.com. Keys start with KEY. |
| Model not available | Error 10027: model not found. | Check available models at the Telnyx Portal. Try meta-llama/Llama-3.3-70B-Instruct as the default. |
| Timeout errors | Inference request exceeds 30 seconds. | Reduce max_tokens, use a smaller model, or increase the timeout. |
| Rate limit (429) | Too many requests. | Add retry logic with exponential backoff. |

## FAQ

**Q: Which models are available on Telnyx Inference?**

Telnyx supports Llama 3.3 70B, Qwen 3, Kimi K2.5, GPT-5, and more. The model list is updated regularly. Check the Telnyx Models page for the current catalog.

**Q: Is the API really OpenAI-compatible?**

Yes. Same request format, same response schema. You can use the OpenAI Python SDK with base_url set to https://api.telnyx.com/v2/ai and your Telnyx API key.

**Q: Can I use this for voice AI agents?**

Yes, and that is where Telnyx inference shines. Because inference runs on the same network as Telnyx telephony, voice AI agents get sub-200ms latency without extra hops. See the Build a Voice AI Agent example.

**Q: What about streaming responses?**

The Telnyx Inference API supports streaming via stream set to true. The response uses server-sent events (SSE), compatible with the OpenAI streaming format.

## Resources

- [Telnyx Inference Documentation](https://developers.telnyx.com/docs/inference)
- [OpenAI-Compatible Chat API](https://developers.telnyx.com/api-reference/openai-chat/create-a-chat-completion-openai-compatible)
- [Python SDK](https://developers.telnyx.com/development/sdk/python)
- [Inference Pricing](https://telnyx.com/pricing/inference)

## Related Examples

- [Build a Voice AI Agent with Python](../build-voice-ai-agent-python/) — Full voice AI agent using Telnyx Inference + Call Control.
- [Create an AI Assistant with Python](../create-ai-assistant-python/) — Managed AI assistant with built-in inference.
- [Chat with AI Assistant with Python](../chat-with-ai-assistant-python/) — Chat interface for Telnyx AI Assistants.
