# SIP Load Balancer Health Check — monitor SIP trunk health across multiple endpoints, auto-failover to healthy trunks, track uptime metrics.

SIP Load Balancer Health Check — monitor SIP trunk health across multiple endpoints, auto-failover to healthy trunks, track uptime metrics.

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
docker build -t sip-load-balancer-health-check .
docker run --env-file .env -p 5000:5000 sip-load-balancer-health-check
```

## API Reference

### `POST /check`

```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /route`

```bash
curl http://localhost:5000/route
```

### `GET /endpoints`

Returns all endpoints.

```bash
curl http://localhost:5000/endpoints
```

### `POST /endpoints`

Create a new record.

```bash
curl -X POST http://localhost:5000/endpoints \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "host": "value",
  "port": "5060",
  "weight": "10"
}'
```

### `GET /log`

```bash
curl http://localhost:5000/log
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
