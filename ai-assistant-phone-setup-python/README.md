---
name: ai-assistant-phone-setup
title: "AI Assistant Phone Setup"
description: "AI Assistant Phone Setup — create and configure a managed Telnyx AI Assistant and wire it to a phone number."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Assistant Phone Setup

AI Assistant Phone Setup — create and configure a managed Telnyx AI Assistant and wire it to a phone number.

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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-assistant-phone-setup-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-assistant-phone-setup .
docker run --env-file .env -p 5000:5000 ai-assistant-phone-setup
```

## API Reference

### `POST /assistants`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/assistants \
  -H "Content-Type: application/json" \
  -d '{
  "name": "My Assistant",
  "instructions": "You are a helpful assistant. Be friendly and concise.",
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "voice_provider": "telnyx",
  "voice_id": "en-US-Neural2-F",
  "speed": "1.0",
  "greeting": "Hello! How can I help you today?",
  "hold_music_url": "https://pay.example.com/inv-123"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /assistants`

Returns all assistants.

**Request:**

```bash
curl http://localhost:5000/assistants
```

**Response:**

```json
{
  "assistants": [
    "..."
  ]
}
```

### `GET /assistants/<assistant_id>`

Returns assistant details.

**Request:**

```bash
curl http://localhost:5000/assistants/example-id
```

**Response:**

```json
{
  "assistant": [
    "..."
  ]
}
```

### `PATCH /assistants/<assistant_id>`

Updates the record.

**Request:**

```bash
curl -X PATCH http://localhost:5000/assistants/example-id
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /assistants/<assistant_id>/wire`

Handles `POST /assistants/<assistant_id>/wire`.

**Request:**

```bash
curl -X POST http://localhost:5000/assistants/example-id/wire
```

**Response:**

```json
{
  "assistant_id": "...",
  "phone_number": "...",
  "instructions": "..."
}
```

### `POST /assistants/<assistant_id>/test`

Handles `POST /assistants/<assistant_id>/test`.

**Request:**

```bash
curl -X POST http://localhost:5000/assistants/example-id/test \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Hello"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /models`

Returns all models.

**Request:**

```bash
curl http://localhost:5000/models
```

**Response:**

```json
{
  "models": [
    "..."
  ]
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
