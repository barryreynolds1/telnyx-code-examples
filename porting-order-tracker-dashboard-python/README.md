# Porting Order Tracker Dashboard â submit, track, and manage porting orders with SLA monitoring, timeline visualization, and bulk operations.

Porting Order Tracker Dashboard â submit, track, and manage porting orders with SLA monitoring, timeline visualization, and bulk operations.

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
docker build -t porting-order-tracker-dashboard .
docker run --env-file .env -p 5000:5000 porting-order-tracker-dashboard
```

## API Reference

### `POST /porting/orders`

```bash
curl -X POST http://localhost:5000/porting/orders \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "+12125551234",
  "authorized_person": "value",
  "current_provider": "abc-123",
  "billing_phone_number": "+12125551234",
  "reference": "value"
}'
```

### `POST /porting/bulk`

```bash
curl -X POST http://localhost:5000/porting/bulk \
  -H "Content-Type: application/json" \
  -d '{
  "batches": "value"
}'
```

### `GET /porting/orders`

Returns all orders.

```bash
curl http://localhost:5000/porting/orders
```

### `GET /porting/sla-check`

```bash
curl http://localhost:5000/porting/sla-check
```

### `GET /porting/dashboard`

Dashboard/analytics view.

```bash
curl http://localhost:5000/porting/dashboard
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

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
