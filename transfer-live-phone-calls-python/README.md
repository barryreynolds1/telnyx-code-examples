# Production-ready Flask application for call transfer via Telnyx Voice API.

Production-ready Flask application for call transfer via Telnyx Voice API.

## Webhook Events Handled

```
call.initiated
call.answered
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
docker build -t transfer-live-phone-calls .
docker run --env-file .env -p 5000:5000 transfer-live-phone-calls
```

## API Reference

### `POST /calls/initiate`

```bash
curl -X POST http://localhost:5000/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /calls/transfer`

```bash
curl -X POST http://localhost:5000/calls/transfer \
  -H "Content-Type: application/json" \
  -d '{
  "transfer_to": "value"
}'
```

### `POST /calls/hangup`

```bash
curl -X POST http://localhost:5000/calls/hangup \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /calls/status/<call_control_id>`

Update record status.

```bash
curl http://localhost:5000/calls/status/<call_control_id>
```

## Webhook Endpoints

### `POST /webhooks/call-events`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
