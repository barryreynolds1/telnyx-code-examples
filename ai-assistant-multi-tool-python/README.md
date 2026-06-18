---
name: ai-assistant-multi-tool
title: "AI Assistant Multi-Tool"
description: "AI Assistant Multi-Tool — AI Assistant with custom function-calling tools for CRM lookup, appointment booking, and order status."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Assistant Multi-Tool

AI Assistant Multi-Tool — AI Assistant with custom function-calling tools for CRM lookup, appointment booking, and order status.

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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-assistant-multi-tool-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-assistant-multi-tool .
docker run --env-file .env -p 5000:5000 ai-assistant-multi-tool
```

## API Reference

### `POST /chat`

Handles `POST /chat`.

**Request:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
  "messages": "[]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /tools`

Returns all tools.

**Request:**

```bash
curl http://localhost:5000/tools
```

**Response:**

```json
{
  "tools": "..."
}
```

### `GET /tool-calls`

Returns all tool calls.

**Request:**

```bash
curl http://localhost:5000/tool-calls
```

**Response:**

```json
{
  "calls": "..."
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
