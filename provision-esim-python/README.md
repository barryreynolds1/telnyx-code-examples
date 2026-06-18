# Production-ready Flask application for eSIM provisioning via Telnyx.

Production-ready Flask application for eSIM provisioning via Telnyx.

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
docker build -t provision-esim .
docker run --env-file .env -p 5000:5000 provision-esim
```

## API Reference

### `POST /esim/profiles`

```bash
curl -X POST http://localhost:5000/esim/profiles \
  -H "Content-Type: application/json" \
  -d '{
  "device_name": "Jane Doe",
  "sim_card_group_id": "abc-123"
}'
```

### `POST /esim/profiles/<sim_card_id>/activate`

```bash
curl -X POST http://localhost:5000/esim/profiles/<sim_card_id>/activate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /esim/profiles/<sim_card_id>`

```bash
curl http://localhost:5000/esim/profiles/<sim_card_id>
```

### `GET /esim/profiles`

Returns all esims.

```bash
curl http://localhost:5000/esim/profiles
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

### `POST /esim/webhooks/sim-status`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
