# Billing Anomaly Detector — monitor usage and billing for anomalies, alert on cost spikes and unusual patterns.

Billing Anomaly Detector — monitor usage and billing for anomalies, alert on cost spikes and unusual patterns.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `ALERT_WEBHOOK` | string | `https://...` | **yes** | alert webhook |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t billing-anomaly-detector .
docker run --env-file .env -p 5000:5000 billing-anomaly-detector
```

## API Reference

### `POST /config`

```bash
curl -X POST http://localhost:5000/config \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /config`

```bash
curl http://localhost:5000/config
```

### `POST /check`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /balance`

```bash
curl http://localhost:5000/balance
```

### `GET /alerts`

Returns all alerts.

```bash
curl http://localhost:5000/alerts
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
