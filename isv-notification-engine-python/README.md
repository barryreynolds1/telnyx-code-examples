# ISV Notification Engine

SaaS platform sends alerts via SMS/voice/WhatsApp based on customer preference and urgency. Multi-channel with fallback cascade and delivery tracking.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |

## Webhook Events Handled

```
call.answered
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
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `WHATSAPP_NUMBER` | string | `+E.164` | no | WhatsApp-enabled Telnyx number ([get it](https://portal.telnyx.com/numbers)) |

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
docker build -t isv-notification-engine .
docker run --env-file .env -p 5000:5000 isv-notification-engine
```

## API Reference

### `POST /notify`

```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{
  "customer_id": "abc-123",
  "message": "Hello, this is a test",
  "urgency": "normal"
}'
```

### `POST /notify/bulk`

```bash
curl -X POST http://localhost:5000/notify/bulk \
  -H "Content-Type: application/json" \
  -d '{
  "customer_ids": "abc-123",
  "message": "Hello, this is a test",
  "urgency": "normal"
}'
```

### `GET /customers`

Returns all customers.

```bash
curl http://localhost:5000/customers
```

### `PUT /customers/<cid>/preference`

Update record status.

```bash
curl -X PUT http://localhost:5000/customers/<cid>/preference \
  -H "Content-Type: application/json" \
  -d '{
  "preference": "customers[cid][\"preference\"]",
  "fallback": "customers[cid].get(\"fallback\", []"
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

Events handled: `call.answered`

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

- [Call Control: Speak](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
