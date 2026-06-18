# SMS Drip Campaign Engine — multi-step nurture sequences with branch logic and AI personalization.

SMS Drip Campaign Engine — multi-step nurture sequences with branch logic and AI personalization.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
message.received
```

## How It Works

```
Inbound SMS ──► Telnyx ──► POST /webhooks/sms
                                   │
                                   ├── AI categorizes/responds
                                   ├── Takes action
                                   └── Sends reply SMS
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `CAMPAIGN_NUMBER` | string | `+E.164` | **yes** | campaign number |
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
docker build -t sms-drip-campaign-engine .
docker run --env-file .env -p 5000:5000 sms-drip-campaign-engine
```

## API Reference

### `POST /drip/create`

Create a new record.

```bash
curl -X POST http://localhost:5000/drip/create \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "steps": "value"
}'
```

### `POST /drip/<did>/subscribe`

```bash
curl -X POST http://localhost:5000/drip/<did>/subscribe \
  -H "Content-Type: application/json" \
  -d '{
  "phone": "+12125551234"
}'
```

### `POST /drip/advance`

```bash
curl -X POST http://localhost:5000/drip/advance \
  -H "Content-Type: application/json" \
  -d '{}'
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
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
