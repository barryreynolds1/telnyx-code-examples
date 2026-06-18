# Production-ready Flask application for call forwarding via Telnyx Voice API.

Production-ready Flask application for call forwarding via Telnyx Voice API.

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
| `FORWARD_TO_NUMBER` | string | `+E.164` | **yes** | forward to number |
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
docker build -t call-forwarding .
docker run --env-file .env -p 5000:5000 call-forwarding
```

## API Reference

### `GET /calls/status/<call_control_id>`

Update record status.

```bash
curl http://localhost:5000/calls/status/<call_control_id>
```

### `POST /calls/hangup/<call_control_id>`

```bash
curl -X POST http://localhost:5000/calls/hangup/<call_control_id> \
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

### `POST /webhooks/call`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
