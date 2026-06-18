# Production-ready Flask application for managing conference calls via Telnyx.

Production-ready Flask application for managing conference calls via Telnyx.

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
docker build -t build-conference-calling .
docker run --env-file .env -p 5000:5000 build-conference-calling
```

## API Reference

### `POST /conference/create`

Create a new record.

```bash
curl -X POST http://localhost:5000/conference/create \
  -H "Content-Type: application/json" \
  -d '{
  "conference_name": "Jane Doe",
  "participants": "value"
}'
```

### `POST /conference/<conference_name>/add-participant`

Create a new record.

```bash
curl -X POST http://localhost:5000/conference/<conference_name>/add-participant \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `POST /conference/<conference_name>/end`

```bash
curl -X POST http://localhost:5000/conference/<conference_name>/end \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /conference/<conference_name>/status`

Update record status.

```bash
curl http://localhost:5000/conference/<conference_name>/status
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

### `POST /webhooks/call-events`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
