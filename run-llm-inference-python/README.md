---
name: run-llm-inference
title: "Run LLM inference on Telnyx — OpenAI-compatible chat completions API."
description: "Run LLM inference on Telnyx — OpenAI-compatible chat completions API."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Run LLM inference on Telnyx — OpenAI-compatible chat completions API.

Run LLM inference on Telnyx — OpenAI-compatible chat completions API.

## Telnyx API Endpoints Used

- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
                                                   │
                                          ┌────────┴────────┐
                                          │ Telnyx Inference │
                                          │ (AI processing) │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Response (SMS/  │
                                          │ Voice/Webhook)  │
                                          └─────────────────┘
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Type | Example | Required | Description | Where to get it |
|----------|------|---------|----------|-------------|-----------------|
| `TELNYX_API_KEY` | `string` | `KEY...` | **yes** | Telnyx API v2 key | [→ link](https://portal.telnyx.com/api-keys) |
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |
| `FLASK_DEBUG` | `string` | `false` | no | flask debug | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/run-llm-inference-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t run-llm-inference .
docker run --env-file .env -p 5000:5000 run-llm-inference
```

## API Reference

### `POST /inference/chat`

Handles `POST /inference/chat`.

**Request:**

```bash
curl -X POST http://localhost:5000/inference/chat \
  -H "Content-Type: application/json" \
  -d '{
  "model": "example_value",
  "max_tokens": 500,
  "temperature": "0.7"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /inference/ask`

Handles `POST /inference/ask`.

**Request:**

```bash
curl -X POST http://localhost:5000/inference/ask \
  -H "Content-Type: application/json" \
  -d '{
  "system_prompt": "example_value"
}'
```

**Response:**

```json
{
  "answer": "..."
}
```

### `GET /health`

Returns service health and operational metrics.

**Request:**

```bash
curl http://localhost:5000/health
```

**Response:**

```json
{
  "status": "ok"
}
```

## Resources

- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
