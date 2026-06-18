# Production-ready Flask application for sending bulk SMS via Telnyx.

Production-ready Flask application for sending bulk SMS via Telnyx.

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
| `BULK_SMS_RATE_LIMIT` | string | `-` | no | bulk sms rate limit |
| `BULK_SMS_DELAY` | string | `-` | no | bulk sms delay |
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
docker build -t send-bulk-sms .
docker run --env-file .env -p 5000:5000 send-bulk-sms
```

## API Reference

### `POST /sms/bulk/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/sms/bulk/send \
  -H "Content-Type: application/json" \
  -d '{
  "recipients": "value",
  "message": "Hello, this is a test"
}'
```

### `GET /sms/bulk/status`

Update record status.

```bash
curl http://localhost:5000/sms/bulk/status
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
