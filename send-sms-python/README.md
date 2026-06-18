# Production-ready Flask endpoint for sending SMS via Telnyx.

Production-ready Flask endpoint for sending SMS via Telnyx.

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
| `TELNYX_PHONE_NUMBER` | string | `+E.164` | **yes** | telnyx phone number |
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

- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t send-sms .
docker run --env-file .env -p 5000:5000 send-sms
```

## API Reference

### `POST /sms/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/sms/send \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Hello, this is a test"
}'
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
