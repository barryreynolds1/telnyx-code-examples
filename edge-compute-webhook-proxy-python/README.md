---
name: edge-compute-webhook-proxy
title: "Edge Compute Webhook Proxy"
description: "Local dev server for testing webhook routing logic before deploying to Telnyx Edge. Includes the Edge function source and deployment instructions."
language: python
framework: flask
---

# Edge Compute Webhook Proxy

Local dev server for testing webhook routing logic before deploying to Telnyx Edge. Includes the Edge function source and deployment instructions.

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers
- `call.answered` — call connected, app speaks greeting
- `call.speak.ended` — TTS finished, app starts listening
- `call.gather.ended` — caller input received (speech or DTMF)
- `call.hangup` — call ended, app cleans up session
- `message.received` — inbound SMS/MMS received

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
| `VOICE_HANDLER_URL` | `string` | `https://...` | no | voice handler url | — |
| `MESSAGE_HANDLER_URL` | `string` | `https://...` | no | message handler url | — |
| `DEFAULT_HANDLER_URL` | `string` | `https://...` | no | default handler url | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/edge-compute-webhook-proxy-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t edge-compute-webhook-proxy .
docker run --env-file .env -p 5000:5000 edge-compute-webhook-proxy
```

## API Reference

### `GET /edge-source`

Handles `GET /edge-source`.

**Request:**

```bash
curl http://localhost:5000/edge-source
```

**Response:**

```json
{
  "source": "...",
  "deploy": "...",
  "note": "..."
}
```

### `GET /routes`

Returns all routes.

**Request:**

```bash
curl http://localhost:5000/routes
```

**Response:**

```json
{
  "routes": [
    "..."
  ]
}
```

### `GET /stats`

Returns analytics and aggregate metrics.

**Request:**

```bash
curl http://localhost:5000/stats
```

**Response:**

```json
{
  "stats": {
    "total": 12,
    "completed": 8
  },
  "total": 3,
  "recent": "..."
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

## Webhook Endpoints

### `POST /webhook`

Receives external webhook events.

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
