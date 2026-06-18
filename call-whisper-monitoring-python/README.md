# Production-ready Flask application for Whisper-based call prompts via Telnyx.

Production-ready Flask application for Whisper-based call prompts via Telnyx.

## Webhook Events Handled

```
call.answered
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
| `OPENAI_API_KEY` | string | `token` | **yes** | openai api key |
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
docker build -t call-whisper-monitoring .
docker run --env-file .env -p 5000:5000 call-whisper-monitoring
```

## API Reference

### `POST /calls/initiate`

```bash
curl -X POST http://localhost:5000/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /calls/<call_control_id>/status`

Update record status.

```bash
curl http://localhost:5000/calls/<call_control_id>/status
```

## Webhook Endpoints

### `POST /webhooks/call`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
