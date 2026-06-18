---
name: chat-with-ai-assistant
title: "Production-ready Flask endpoint for chatting with Telnyx AI Assistants."
description: "Production-ready Flask endpoint for chatting with Telnyx AI Assistants."
language: python
framework: flask
---

# Production-ready Flask endpoint for chatting with Telnyx AI Assistants.

Production-ready Flask endpoint for chatting with Telnyx AI Assistants.

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
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
| `AI_ASSISTANT_ID` | `string` | `...` | **yes** | ai assistant id | — |
| `FLASK_DEBUG` | `string` | `false` | no | flask debug | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t chat-with-ai-assistant .
docker run --env-file .env -p 5000:5000 chat-with-ai-assistant
```

## API Reference

### `POST /chat`

Handles `POST /chat`.

**Request:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Customer reported issue with service",
  "assistant_id": "abc-123"
}'
```

**Response:**

```json
{
  "status_code": "..."
}
```

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
