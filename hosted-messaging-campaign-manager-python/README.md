# Hosted Messaging Campaign Manager — manage hosted messaging campaigns with subscriber opt-in/out tracking and delivery analytics.

Hosted Messaging Campaign Manager — manage hosted messaging campaigns with subscriber opt-in/out tracking and delivery analytics.

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
| `FROM_NUMBER` | string | `+E.164` | **yes** | from number |
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
docker build -t hosted-messaging-campaign-manager .
docker run --env-file .env -p 5000:5000 hosted-messaging-campaign-manager
```

## API Reference

### `POST /campaigns`

Create a new record.

```bash
curl -X POST http://localhost:5000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "message": "Hello, this is a test"
}'
```

### `POST /subscribers`

Create a new record.

```bash
curl -X POST http://localhost:5000/subscribers \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "+12125551234"
}'
```

### `POST /campaigns/<cid>/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/campaigns/<cid>/send \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /subscribers`

Returns all subscribers.

```bash
curl http://localhost:5000/subscribers
```

### `GET /campaigns`

Returns all campaigns.

```bash
curl http://localhost:5000/campaigns
```

### `GET /analytics`

```bash
curl http://localhost:5000/analytics
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

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
