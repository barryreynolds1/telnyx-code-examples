# Number Porting Status Tracker — track porting orders with status webhooks and SMS alerts.

Number Porting Status Tracker — track porting orders with status webhooks and SMS alerts.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `ALERT_NUMBER` | string | `+E.164` | **yes** | alert number |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t number-porting-status-tracker .
docker run --env-file .env -p 5000:5000 number-porting-status-tracker
```

## API Reference

### `GET /ports/list`

Returns all ports.

```bash
curl http://localhost:5000/ports/list
```

### `POST /ports/create`

Create a new record.

```bash
curl -X POST http://localhost:5000/ports/create \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "+12125551234"
}'
```

### `GET /ports/<order_id>`

```bash
curl http://localhost:5000/ports/<order_id>
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

### `POST /webhooks/porting`

Receives external webhook events.

## Resources

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
