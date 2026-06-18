# Production-ready Flask application for monitoring SIM card data usage via Telnyx IoT API.

Production-ready Flask application for monitoring SIM card data usage via Telnyx IoT API.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `DATA_LIMIT_THRESHOLD_MB` | integer | `-` | no | data limit threshold mb |
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
docker build -t monitor-iot-data-usage .
docker run --env-file .env -p 5000:5000 monitor-iot-data-usage
```

## API Reference

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

### `GET /sim-cards`

Returns all sims.

```bash
curl http://localhost:5000/sim-cards
```

### `GET /sim-cards/<sim_card_id>`

```bash
curl http://localhost:5000/sim-cards/<sim_card_id>
```

### `GET /sim-cards/<sim_card_id>/usage`

```bash
curl http://localhost:5000/sim-cards/<sim_card_id>/usage
```

### `GET /sim-cards/<sim_card_id>/health`

Health check and service status.

```bash
curl http://localhost:5000/sim-cards/<sim_card_id>/health
```

```json
{"status": "ok"}
```

### `POST /sim-cards/<sim_card_id>/activate`

```bash
curl -X POST http://localhost:5000/sim-cards/<sim_card_id>/activate \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Webhook Endpoints

### `POST /webhooks/sim-events`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
