---
name: iot-panic-button-voice-alert
title: "IoT Panic Button Voice Alert"
description: "IoT Panic Button Voice Alert — IoT device triggers SIM-based alert, system calls emergency contacts with location and status."
language: python
framework: flask
telnyx_products: [SMS/MMS, Voice]
channel: [voice]
---

# IoT Panic Button Voice Alert

IoT Panic Button Voice Alert — IoT device triggers SIM-based alert, system calls emergency contacts with location and status.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)
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
| `ALERT_NUMBER` | `string` | `+18005551234` | **yes** | alert number | — |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/iot-panic-button-voice-alert-python
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
docker build -t iot-panic-button-voice-alert .
docker run --env-file .env -p 5000:5000 iot-panic-button-voice-alert
```

## API Reference

### `POST /alert`

Triggers the workflow. Returns execution results.

**Request:**

```bash
curl -X POST http://localhost:5000/alert \
  -H "Content-Type: application/json" \
  -d '{
  "device_id": "abc-123"
}'
```

**Response:**

```json
{
  "alert_id": "...",
  "contacts_notified": "..."
}
```

### `POST /devices`

Handles `POST /devices`.

**Request:**

```bash
curl -X POST http://localhost:5000/devices \
  -H "Content-Type: application/json" \
  -d '{
  "device_id": "f\"DEV-{int(time.time(",
  "name": "Jane Doe",
  "location": "example_value",
  "contacts": "[]"
}'
```

**Response:**

```json
{
  "device_id": "..."
}
```

### `GET /alerts`

Returns all alerts.

**Request:**

```bash
curl http://localhost:5000/alerts
```

**Response:**

```json
{
  "alerts": "..."
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

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Call Control: Dial — API Reference](https://developers.telnyx.com/api/call-control/dial)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
