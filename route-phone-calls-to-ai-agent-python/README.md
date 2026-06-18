# Production-ready Flask webhook for handling inbound calls via Telnyx Voice API.

Production-ready Flask webhook for handling inbound calls via Telnyx Voice API.

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.hangup
```

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
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
docker build -t route-phone-calls-to-ai-agent .
docker run --env-file .env -p 5000:5000 route-phone-calls-to-ai-agent
```

## Webhook Endpoints

### `POST /webhooks/call`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
