# Production-ready Flask application for text-to-speech calls via Telnyx.

Production-ready Flask application for text-to-speech calls via Telnyx.

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.hangup
call.gather.ended (speech)
```

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `TELNYX_PHONE_NUMBER` | string | `+E.164` | **yes** | telnyx phone number |
| `TELNYX_CONNECTION_ID` | string | `-` | **yes** | telnyx connection id |
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
docker build -t text-to-speech-phone-call .
docker run --env-file .env -p 5000:5000 text-to-speech-phone-call
```

## API Reference

### `POST /calls/initiate`

```bash
curl -X POST http://localhost:5000/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /calls/<call_control_id>/speak`

```bash
curl -X POST http://localhost:5000/calls/<call_control_id>/speak \
  -H "Content-Type: application/json" \
  -d '{
  "text": "Hello, this is a test",
  "language": "en-US"
}'
```

### `POST /calls/<call_control_id>/hangup`

```bash
curl -X POST http://localhost:5000/calls/<call_control_id>/hangup \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /calls/status`

Update record status.

```bash
curl http://localhost:5000/calls/status
```

## Webhook Endpoints

### `POST /webhooks/call`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
