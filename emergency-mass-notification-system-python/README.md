# Emergency Mass Notification System — SMS + voice calls with delivery tracking and escalation.

Emergency Mass Notification System — SMS + voice calls with delivery tracking and escalation.

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
call.gather.ended (DTMF)
```

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → process → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `ALERT_NUMBER` | string | `+E.164` | **yes** | alert number |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |

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

### Docker

```bash
docker build -t emergency-mass-notification-system .
docker run --env-file .env -p 5000:5000 emergency-mass-notification-system
```

## API Reference

### `POST /notify`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Hello, this is a test",
  "contacts": "value",
  "severity": "normal"
}'
```

### `GET /notifications`

Returns all notifications.

```bash
curl http://localhost:5000/notifications
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
