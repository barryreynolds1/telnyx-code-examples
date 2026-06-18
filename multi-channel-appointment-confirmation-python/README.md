# Multi-Channel Appointment Confirmation — confirm appointments via SMS, voice call, and WhatsApp. Tries SMS first, escalates to voice if no response.

Multi-Channel Appointment Confirmation — confirm appointments via SMS, voice call, and WhatsApp. Tries SMS first, escalates to voice if no response.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |
| Call Control API | `POST /v2/calls` | [docs](https://developers.telnyx.com/docs/voice/call-control) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.gather.ended
call.hangup
message.received
call.gather.ended (DTMF)
```

## How It Works

```
Inbound Call/SMS ──► Telnyx ──► POST /webhooks/voice or /webhooks/sms
                                        │
                                        │
                                        ▼
                                  Response / Action
                                  (speak, SMS, dispatch)
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `CONFIRM_NUMBER` | string | `+E.164` | **yes** | confirm number |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `MESSAGING_PROFILE_ID` | string | `uuid` | no | Telnyx messaging profile ID ([get it](https://portal.telnyx.com/messaging/profiles)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Webhook URL

Expose with [ngrok](https://ngrok.com): `ngrok http 5000`

Configure in [Telnyx Portal](https://portal.telnyx.com):

- **Call Control App** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/voice`
- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t multi-channel-appointment-confirmation .
docker run --env-file .env -p 5000:5000 multi-channel-appointment-confirmation
```

## API Reference

### `POST /appointments`

Create a new record.

```bash
curl -X POST http://localhost:5000/appointments \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "phone": "+12125551234",
  "date": "2026-07-01",
  "time": "09:00",
  "provider": "Dr. Smith"
}'
```

### `POST /confirm/<aid>`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/confirm/<aid> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /escalate/<aid>`

```bash
curl -X POST http://localhost:5000/escalate/<aid> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /appointments/status`

Update record status.

```bash
curl http://localhost:5000/appointments/status
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Webhook Endpoints

### `POST /webhooks/messaging`

Receives Telnyx Messaging webhook events.

Example payload:

```json
{
  "data": {
    "event_type": "message.received",
    "payload": {
      "from": {
        "phone_number": "+12125551234"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "Hello",
      "media": []
    }
  }
}
```

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (DTMF)`

Example payload:

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:abc-123",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876"
  }
}
```

## Resources

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [Call Control API](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
