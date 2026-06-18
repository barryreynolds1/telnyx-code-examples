# SMS Emergency Check-In — periodic wellness checks via SMS with escalation to emergency contacts.

SMS Emergency Check-In — periodic wellness checks via SMS with escalation to emergency contacts.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |

## Webhook Events Handled

```
message.received
```

## How It Works

```
Inbound SMS ──► Telnyx ──► POST /webhooks/sms
                                   │
                                   ├── Takes action
                                   └── Sends reply SMS
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `CHECK_IN_NUMBER` | string | `+E.164` | **yes** | check in number |
| `EMERGENCY_CONTACT` | string | `-` | **yes** | emergency contact |
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

- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t sms-emergency-check-in .
docker run --env-file .env -p 5000:5000 sms-emergency-check-in
```

## API Reference

### `POST /monitor`

Create a new record.

```bash
curl -X POST http://localhost:5000/monitor \
  -H "Content-Type: application/json" \
  -d '{
  "phone": "+12125551234",
  "name": "Jane Doe",
  "emergency_contact": "EMERGENCY_CONTACT"
}'
```

### `POST /check-in/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/check-in/send \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /check-in/escalate`

```bash
curl -X POST http://localhost:5000/check-in/escalate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /status`

Update record status.

```bash
curl http://localhost:5000/status
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

## Resources

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
