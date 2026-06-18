---
name: webhook-debugger-ai-assistant
title: "Webhook Debugger AI Assistant"
description: "Webhook Debugger AI Assistant — catch, inspect, and debug Telnyx webhooks with AI explanations."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Webhook Debugger AI Assistant

Webhook Debugger AI Assistant — catch, inspect, and debug Telnyx webhooks with AI explanations.

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
cd telnyx-code-examples/webhook-debugger-ai-assistant-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t webhook-debugger-ai-assistant .
docker run --env-file .env -p 5000:5000 webhook-debugger-ai-assistant
```

## API Reference

### `GET /catch/<path:subpath>`

Handles `GET /catch/<path:subpath>`.

**Request:**

```bash
curl http://localhost:5000/catch/example-id
```

**Response:**

```json
{
  "status": "ok",
  "id": "..."
}
```

### `POST /catch/<path:subpath>`

Handles `POST /catch/<path:subpath>`.

**Request:**

```bash
curl -X POST http://localhost:5000/catch/example-id
```

**Response:**

```json
{
  "status": "ok",
  "id": "..."
}
```

### `PUT /catch/<path:subpath>`

Handles `PUT /catch/<path:subpath>`.

**Request:**

```bash
curl -X PUT http://localhost:5000/catch/example-id
```

**Response:**

```json
{
  "status": "ok",
  "id": "..."
}
```

### `DELETE /catch/<path:subpath>`

Handles `DELETE /catch/<path:subpath>`.

**Response:**

```json
{
  "status": "ok",
  "id": "..."
}
```

### `GET /analyze/<int:index>`

Handles `GET /analyze/<int:index>`.

**Request:**

```bash
curl http://localhost:5000/analyze/example-id
```

**Response:**

```json
{
  "webhook": "...",
  "analysis": "..."
}
```

### `GET /analyze/recent`

Handles `GET /analyze/recent`.

**Request:**

```bash
curl http://localhost:5000/analyze/recent
```

**Response:**

```json
{
  "recent_count": 3,
  "analysis": "..."
}
```

### `GET /log`

Handles `GET /log`.

**Request:**

```bash
curl http://localhost:5000/log
```

**Response:**

```json
{
  "webhooks": "...",
  "total": 3
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
