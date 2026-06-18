# Production-ready Flask endpoint for sending MMS via Telnyx.

Production-ready Flask endpoint for sending MMS via Telnyx.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| MMS Media | `via Messaging API` | [docs](https://developers.telnyx.com/docs/messaging) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
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

### Docker

```bash
docker build -t send-mms-picture-message .
docker run --env-file .env -p 5000:5000 send-mms-picture-message
```

## API Reference

### `POST /mms/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/mms/send \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Hello, this is a test",
  "media_urls": "value"
}'
```

## Resources

- [MMS Media](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
