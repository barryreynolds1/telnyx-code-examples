---
name: multi-channel-appointment-confirmation
title: "Multi-Channel Appointment Confirmation"
description: "Multi-Channel Appointment Confirmation — confirm appointments via SMS, voice call, and WhatsApp. Tries SMS first, escalates to voice if no response."
language: python
framework: flask
telnyx_products: [SMS/MMS, Voice]
channel: [voice, sms]
---

# Multi-Channel Appointment Confirmation

Multi-Channel Appointment Confirmation — confirm appointments via SMS, voice call, and WhatsApp. Tries SMS first, escalates to voice if no response.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)
- **Call Control: Dial**: `POST /v2/calls` — [API reference](https://developers.telnyx.com/api/call-control/dial)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.answered` — call connected, app speaks greeting
- `call.speak.ended` — TTS finished, app starts listening
- `call.gather.ended` — caller input received (speech or DTMF)
- `call.hangup` — call ended, app cleans up session
- `message.received` — inbound SMS/MMS received

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│  Phone Call  │────►│            │────►│  POST /webhooks/voice│
│  or SMS/MMS  │     │   Telnyx   │     │  POST /webhooks/sms  │
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
| `CONFIRM_NUMBER` | `string` | `+18005551234` | **yes** | confirm number | — |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |
| `MESSAGING_PROFILE_ID` | `string` | `4001...` | no | Telnyx messaging profile ID | [→ link](https://portal.telnyx.com/messaging/profiles) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/multi-channel-appointment-confirmation-python
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
   - **Messaging Profile** → Inbound Webhook URL → `https://<id>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t multi-channel-appointment-confirmation .
docker run --env-file .env -p 5000:5000 multi-channel-appointment-confirmation
```

## API Reference

### `POST /appointments`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/appointments \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "phone": "+12125551234",
  "date": "2026-07-15",
  "time": "14:00",
  "provider": "Dr. Smith"
}'
```

**Response:**

```json
{
  "appointment_id": "..."
}
```

### `POST /confirm/<aid>`

Sends notifications to applicable recipients.

**Request:**

```bash
curl -X POST http://localhost:5000/confirm/example-id
```

**Response:**

```json
{
  "status": "ok",
  "success": "..."
}
```

### `POST /escalate/<aid>`

Handles `POST /escalate/<aid>`.

**Request:**

```bash
curl -X POST http://localhost:5000/escalate/example-id
```

**Response:**

```json
{
  "status": "ok",
  "success": "..."
}
```

### `GET /appointments/status`

Handles `GET /appointments/status`.

**Request:**

```bash
curl http://localhost:5000/appointments/status
```

**Response:**

```json
{
  "appointments": "...",
  "summary": "...",
  "confirmations": "..."
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

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Call Control: Dial — API Reference](https://developers.telnyx.com/api/call-control/dial)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
