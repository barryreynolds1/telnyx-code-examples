# IoT Fleet Alert Escalation — severity-based routing from IoT sensors to SMS, calls, and multi-party conferences.

IoT Fleet Alert Escalation — severity-based routing from IoT sensors to SMS, calls, and multi-party conferences.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |
| Call Control API | `POST /v2/calls` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.hangup
```

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → AI inference → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `ALERT_NUMBER` | string | `+E.164` | **yes** | alert number |
| `ONCALL_NUMBER` | string | `+E.164` | **yes** | oncall number |
| `DISPATCHER_NUMBER` | string | `+E.164` | **yes** | dispatcher number |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `FLASK_DEBUG` | string | `-` | no | flask debug |

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
docker build -t iot-fleet-alert-escalation .
docker run --env-file .env -p 5000:5000 iot-fleet-alert-escalation
```

## API Reference

### `POST /alert`

```bash
curl -X POST http://localhost:5000/alert \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /alerts`

Returns all alerts.

```bash
curl http://localhost:5000/alerts
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

Events handled: `call.answered`, `call.speak.ended`, `call.hangup`

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
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
