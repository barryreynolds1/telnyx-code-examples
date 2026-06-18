---
name: sms-emergency-check-in
title: "SMS Emergency Check-In"
description: "SMS Emergency Check-In — periodic wellness checks via SMS with escalation to emergency contacts."
language: python
framework: flask
telnyx_products: [SMS/MMS]
channel: [sms]
---

# SMS Emergency Check-In

SMS Emergency Check-In — periodic wellness checks via SMS with escalation to emergency contacts.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `message.received` — inbound SMS/MMS received

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│   SMS/MMS   │────►│   Telnyx   │────►│  POST /webhooks/sms  │
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
| `CHECK_IN_NUMBER` | `string` | `+18005551234` | **yes** | check in number | — |
| `EMERGENCY_CONTACT` | `string` | `...` | **yes** | emergency contact | — |
| `MESSAGING_PROFILE_ID` | `string` | `4001...` | no | Telnyx messaging profile ID | [→ link](https://portal.telnyx.com/messaging/profiles) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sms-emergency-check-in-python
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

   - **Messaging Profile** → Inbound Webhook URL → `https://<id>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t sms-emergency-check-in .
docker run --env-file .env -p 5000:5000 sms-emergency-check-in
```

## API Reference

### `POST /monitor`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/monitor \
  -H "Content-Type: application/json" \
  -d '{
  "phone": "+12125551234",
  "name": "Jane Doe",
  "emergency_contact": "EMERGENCY_CONTACT"
}'
```

**Response:**

```json
{
  "status": "ok",
  "phone": "..."
}
```

### `POST /check-in/send`

Sends notifications to applicable recipients.

**Request:**

```bash
curl -X POST http://localhost:5000/check-in/send
```

**Response:**

```json
{
  "sent": "..."
}
```

### `POST /check-in/escalate`

Handles `POST /check-in/escalate`.

**Request:**

```bash
curl -X POST http://localhost:5000/check-in/escalate
```

**Response:**

```json
{
  "escalated": "..."
}
```

### `GET /status`

Returns status details.

**Request:**

```bash
curl http://localhost:5000/status
```

**Response:**

```json
{
  "status": [
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

### `POST /webhooks/messaging`

Receives [Telnyx Messaging](https://developers.telnyx.com/docs/messaging) webhook events.

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "message.received",
    "direction": "inbound",
    "payload": {
      "id": "f5d7a7e0-1234-5678-9abc-def012345678",
      "from": {
        "phone_number": "+12125551234",
        "carrier": "Verizon",
        "line_type": "Wireless"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "HELP",
      "type": "SMS",
      "media": [],
      "received_at": "2026-07-15T14:30:00Z"
    }
  }
}
```

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
