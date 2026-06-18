---
name: number-lookup-fraud-screener
title: "Number Lookup Fraud Screener"
description: "Number Lookup Fraud Screener — screen inbound calls/messages for fraud indicators using number lookup before connecting."
language: python
framework: flask
telnyx_products: [Number Lookup]
channel: [voice]
---

# Number Lookup Fraud Screener

Number Lookup Fraud Screener — screen inbound calls/messages for fraud indicators using number lookup before connecting.

## Telnyx API Endpoints Used

- **Number Lookup**: `GET /v2/number_lookup/{phone_number}` — [API reference](https://developers.telnyx.com/api/number-lookup/lookup)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers

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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/number-lookup-fraud-screener-python
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
docker build -t number-lookup-fraud-screener .
docker run --env-file .env -p 5000:5000 number-lookup-fraud-screener
```

## API Reference

### `GET /screen/<number>`

Handles `GET /screen/<number>`.

**Request:**

```bash
curl http://localhost:5000/screen/example-id
```

**Response:**

```json
{
  "number": "...",
  "action": "...",
  "reason": "..."
}
```

### `POST /blocklist`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/blocklist \
  -H "Content-Type: application/json" \
  -d '{
  "number": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok",
  "number": "..."
}
```

### `GET /blocklist`

Returns all blocklist.

**Request:**

```bash
curl http://localhost:5000/blocklist
```

**Response:**

```json
{
  "blocked": "..."
}
```

### `GET /screening-log`

Returns log details.

**Request:**

```bash
curl http://localhost:5000/screening-log
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

**Events handled:** `call.initiated`

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

- [Number Lookup — API Reference](https://developers.telnyx.com/api/number-lookup/lookup)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
