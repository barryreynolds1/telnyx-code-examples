---
name: media-stream-voice-cloak
title: "Media Stream Voice Cloak"
description: "Media Stream Voice Cloak — real-time voice modification via media streaming API. Apply pitch shift, echo, or anonymization."
language: python
framework: flask
telnyx_products: [Voice]
channel: [voice]
---

# Media Stream Voice Cloak

Media Stream Voice Cloak — real-time voice modification via media streaming API. Apply pitch shift, echo, or anonymization.

## Telnyx API Endpoints Used

- **Call Control: Answer**: `POST /v2/calls/{call_control_id}/actions/answer` — [API reference](https://developers.telnyx.com/api/call-control/answer-call)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers
- `call.answered` — call connected, app speaks greeting
- `call.hangup` — call ended, app cleans up session

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│  Phone Call  │────►│   Telnyx   │────►│  POST /webhooks/voice│
└─────────────┘     │   Cloud    │     └──────────┬───────────┘
                    └────────────┘                │
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
| `STREAM_WEBSOCKET_URL` | `string` | `https://...` | no | stream websocket url | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/media-stream-voice-cloak-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Webhook Configuration

1. Expose your local server:

   ```bash
   ngrok http 5000
   ```

2. Copy the HTTPS URL and configure in [Telnyx Portal](https://portal.telnyx.com):

   - **Call Control Application** → Webhook URL → `https://<id>.ngrok.io/webhooks/voice`

### Docker

```bash
docker build -t media-stream-voice-cloak .
docker run --env-file .env -p 5000:5000 media-stream-voice-cloak
```

## API Reference

### `POST /cloak/<ccid>`

Handles `POST /cloak/<ccid>`.

**Request:**

```bash
curl -X POST http://localhost:5000/cloak/example-id \
  -H "Content-Type: application/json" \
  -d '{
  "effect": "anonymous"
}'
```

**Response:**

```json
{
  "status": "ok",
  "effect": "...",
  "config": "..."
}
```

### `GET /effects`

Returns all effects.

**Request:**

```bash
curl http://localhost:5000/effects
```

**Response:**

```json
{
  "effects": "..."
}
```

### `GET /active`

Returns all active.

**Request:**

```bash
curl http://localhost:5000/active
```

**Response:**

```json
{
  "active": 3
}
```

### `GET /log`

Returns log details.

**Request:**

```bash
curl http://localhost:5000/log
```

**Response:**

```json
{
  "log": "..."
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

### `POST /webhooks/voice`

Receives [Telnyx Call Control](https://developers.telnyx.com/docs/voice/call-control) webhook events.

**Events handled:** `call.initiated`, `call.answered`, `call.hangup`

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:uMi2qMWHT-mLFGkEm4t9tA",
    "connection_id": "1494404757140276705",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876",
    "call_leg_id": "428c31b6-7af4-4bcb-b7f5-5013ef9657c1",
    "client_state": null,
    "state": "ringing"
  },
  "meta": {
    "attempt": 1,
    "delivered_to": "https://your-server.example.com/webhooks/voice"
  }
}
```

## Resources

- [Call Control: Answer — API Reference](https://developers.telnyx.com/api/call-control/answer-call)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
