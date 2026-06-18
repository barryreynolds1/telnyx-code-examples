---
name: conference-live-poll-dtmf
title: "Conference Live Poll via DTMF"
description: "Conference Live Poll via DTMF — host asks a question, all conference participants vote by pressing 1-4, results tallied instantly."
language: python
framework: flask
telnyx_products: [Voice]
channel: [voice]
---

# Conference Live Poll via DTMF

Conference Live Poll via DTMF — host asks a question, all conference participants vote by pressing 1-4, results tallied instantly.

## Telnyx API Endpoints Used

- **Call Control: Dial**: `POST /v2/calls` — [API reference](https://developers.telnyx.com/api/call-control/dial)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

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
| `CONF_NUMBER` | `string` | `+18005551234` | **yes** | conf number | — |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/conference-live-poll-dtmf-python
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
docker build -t conference-live-poll-dtmf .
docker run --env-file .env -p 5000:5000 conference-live-poll-dtmf
```

## API Reference

### `POST /conference/create`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/conference/create \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Meeting"
}'
```

**Response:**

```json
{
  "conference_id": "..."
}
```

### `POST /conference/<cid>/invite`

Handles `POST /conference/<cid>/invite`.

**Request:**

```bash
curl -X POST http://localhost:5000/conference/cust-001/invite \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "[]"
}'
```

**Response:**

```json
{
  "invited": "..."
}
```

### `POST /conference/<cid>/poll`

Handles `POST /conference/<cid>/poll`.

**Request:**

```bash
curl -X POST http://localhost:5000/conference/cust-001/poll \
  -H "Content-Type: application/json" \
  -d '{
  "question": "example_value",
  "options": "[]"
}'
```

**Response:**

```json
{
  "poll_id": "..."
}
```

### `GET /conference/<cid>/results`

Handles `GET /conference/<cid>/results`.

**Request:**

```bash
curl http://localhost:5000/conference/example-id/results
```

**Response:**

```json
{
  "message": "...",
  "question": "...",
  "votes": "...",
  "results": "..."
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

**Events handled:** `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`

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

- [Call Control: Dial — API Reference](https://developers.telnyx.com/api/call-control/dial)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
