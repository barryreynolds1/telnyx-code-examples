---
name: isv-notification-engine
title: "ISV Notification Engine"
description: "SaaS platform sends alerts via SMS/voice/WhatsApp based on customer preference and urgency. Multi-channel with fallback cascade and delivery tracking."
language: python
framework: flask
telnyx_products: [Voice]
channel: [voice]
---

# ISV Notification Engine

SaaS platform sends alerts via SMS/voice/WhatsApp based on customer preference and urgency. Multi-channel with fallback cascade and delivery tracking.

## Telnyx API Endpoints Used

- **Call Control: Speak (TTS)**: `POST /v2/calls/{call_control_id}/actions/speak` — [API reference](https://developers.telnyx.com/api/call-control/speak)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.answered` — call connected, app speaks greeting

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
| `MAIN_NUMBER` | `string` | `+18005551234` | **yes** | Telnyx phone number (E.164) | [→ link](https://portal.telnyx.com/numbers/my-numbers) |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |
| `WHATSAPP_NUMBER` | `string` | `+18005551234` | no | WhatsApp-enabled Telnyx number | [→ link](https://portal.telnyx.com/numbers/my-numbers) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/isv-notification-engine-python
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
docker build -t isv-notification-engine .
docker run --env-file .env -p 5000:5000 isv-notification-engine
```

## API Reference

### `POST /notify`

Handles `POST /notify`.

**Request:**

```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{
  "customer_id": "cust-001",
  "message": "Customer reported issue with service",
  "urgency": "normal"
}'
```

**Response:**

```json
{
  "notification": "..."
}
```

### `POST /notify/bulk`

Handles `POST /notify/bulk`.

**Request:**

```bash
curl -X POST http://localhost:5000/notify/bulk \
  -H "Content-Type: application/json" \
  -d '{
  "customer_ids": "[]",
  "message": "Customer reported issue with service",
  "urgency": "normal"
}'
```

**Response:**

```json
{
  "results": "..."
}
```

### `GET /customers`

Returns all customers.

**Request:**

```bash
curl http://localhost:5000/customers
```

**Response:**

```json
{
  "customers": "..."
}
```

### `PUT /customers/<cid>/preference`

Updates the record.

**Request:**

```bash
curl -X PUT http://localhost:5000/customers/cust-001/preference \
  -H "Content-Type: application/json" \
  -d '{
  "preference": "customers[cid][\"preference\"]",
  "fallback": "customers[cid].get(\"fallback\", []"
}'
```

**Response:**

```json
{
  "customer": "..."
}
```

### `GET /notifications`

Returns all notifications.

**Request:**

```bash
curl http://localhost:5000/notifications
```

**Response:**

```json
{
  "notifications": [
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

## Webhook Endpoints

### `POST /webhooks/voice`

Receives [Telnyx Call Control](https://developers.telnyx.com/docs/voice/call-control) webhook events.

**Events handled:** `call.answered`

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

- [Call Control: Speak (TTS) — API Reference](https://developers.telnyx.com/api/call-control/speak)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
