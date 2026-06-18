# Production-ready Flask application for SIM card activation via Telnyx.

Production-ready Flask application for SIM card activation via Telnyx.

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
docker build -t activate-sim-card .
docker run --env-file .env -p 5000:5000 activate-sim-card
```

## API Reference

### `GET /sim-cards`

Returns all sims.

```bash
curl http://localhost:5000/sim-cards
```

### `GET /sim-cards/<sim_card_id>`

```bash
curl http://localhost:5000/sim-cards/<sim_card_id>
```

### `POST /sim-cards/<sim_card_id>/activate`

```bash
curl -X POST http://localhost:5000/sim-cards/<sim_card_id>/activate \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
