---
name: smart-ivr-ab-tester
title: "Smart IVR A/B Tester"
description: "Smart IVR A/B Tester — run two IVR flows simultaneously and track which converts better."
language: python
framework: flask
channel: [voice]
---

# Smart IVR A/B Tester

Smart IVR A/B Tester — run two IVR flows simultaneously and track which converts better.

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers
- `call.answered` — call connected, app speaks greeting
- `call.speak.ended` — TTS finished, app starts listening
- `call.gather.ended` — caller input received (speech or DTMF)
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
| `IVR_NUMBER` | `string` | `+18005551234` | **yes** | ivr number | — |
| `AGENT_NUMBER` | `string` | `+18005551234` | **yes** | agent number | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/smart-ivr-ab-tester-python
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
docker build -t smart-ivr-ab-tester .
docker run --env-file .env -p 5000:5000 smart-ivr-ab-tester
```

## API Reference

### `POST /experiments`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/experiments \
  -H "Content-Type: application/json" \
  -d '{
  "variant_a": "example_value",
  "variant_b": "example_value",
  "split": "0.5"
}'
```

**Response:**

```json
{
  "experiment_id": "..."
}
```

### `GET /experiments/<eid>/results`

Returns results details.

**Request:**

```bash
curl http://localhost:5000/experiments/example-id/results
```

**Response:**

```json
{
  "results": "...",
  "winner": "...",
  "confidence": "..."
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

**Events handled:** `call.initiated`, `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`

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

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
