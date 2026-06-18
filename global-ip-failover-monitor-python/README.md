# Global IP Failover Monitor — monitor Global IP endpoints across regions, auto-failover between healthy endpoints.

Global IP Failover Monitor — monitor Global IP endpoints across regions, auto-failover between healthy endpoints.

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
docker build -t global-ip-failover-monitor .
docker run --env-file .env -p 5000:5000 global-ip-failover-monitor
```

## API Reference

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
  "id": "f\"ep-{int(time.time(",
  "ip_address": "value",
  "region": "value"
}'
```

### `POST /check`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /failover-log`

```bash
curl http://localhost:5000/failover-log
```

### `GET /regions`

```bash
curl http://localhost:5000/regions
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
