# White-Label Appointment Platform

Multi-tenant SaaS that gives any service business their own AI phone line with booking, reminders, and calendar sync. Each tenant has own number, greeting, and config.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Answer | `POST /v2/calls/{id}/actions/answer` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Gather | `POST /v2/calls/{id}/actions/gather` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Hangup | `POST /v2/calls/{id}/actions/hangup` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (speech)
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
docker build -t white-label-appointment-platform .
docker run --env-file .env -p 5000:5000 white-label-appointment-platform
```

## API Reference

### `POST /tenants`

Create a new record.

```bash
curl -X POST http://localhost:5000/tenants \
  -H "Content-Type: application/json" \
  -d '{
  "id": "f\"t-{int(time.time(",
  "business_name": "Jane Doe",
  "phone_number": "+12125551234",
  "greeting": "f\"Thank you for calling {data.get('business_name",
  "services": "value",
  "hours": "Monday-Friday 9AM-5PM",
  "calendar_webhook": "value",
  "notification_phone": "+12125551234"
}'
```

### `GET /tenants`

Returns all tenants.

```bash
curl http://localhost:5000/tenants
```

### `GET /tenants/<tid>/appointments`

```bash
curl http://localhost:5000/tenants/<tid>/appointments
```

### `GET /tenants/<tid>/stats`

Dashboard/analytics view.

```bash
curl http://localhost:5000/tenants/<tid>/stats
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

Events handled: `call.initiated`, `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (speech)`

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

- [Call Control: Answer](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
