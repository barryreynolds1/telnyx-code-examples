# Wireless Fleet Activation Portal — bulk activate SIMs with status tracking.

Wireless Fleet Activation Portal — bulk activate SIMs with status tracking.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t wireless-fleet-activation-portal .
docker run --env-file .env -p 5000:5000 wireless-fleet-activation-portal
```

## API Reference

### `GET /sims`

Returns all sims.

```bash
curl http://localhost:5000/sims
```

### `POST /sims/activate`

```bash
curl -X POST http://localhost:5000/sims/activate \
  -H "Content-Type: application/json" \
  -d '{
  "sim_ids": "abc-123"
}'
```

### `POST /sims/deactivate`

```bash
curl -X POST http://localhost:5000/sims/deactivate \
  -H "Content-Type: application/json" \
  -d '{
  "sim_ids": "abc-123"
}'
```

### `GET /activation-log`

```bash
curl http://localhost:5000/activation-log
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
