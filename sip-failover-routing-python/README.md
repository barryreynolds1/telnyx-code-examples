# Production-ready SIP failover routing system with Flask and Telnyx.

Production-ready SIP failover routing system with Flask and Telnyx.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `PRIMARY_SIP_IP` | string | `-` | **yes** | primary sip ip |
| `PRIMARY_SIP_PORT` | string | `-` | no | primary sip port |
| `BACKUP_SIP_IP` | string | `-` | **yes** | backup sip ip |
| `BACKUP_SIP_PORT` | string | `-` | no | backup sip port |
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
docker build -t sip-failover-routing .
docker run --env-file .env -p 5000:5000 sip-failover-routing
```

## API Reference

### `GET /sip/connections`

Returns all connections.

```bash
curl http://localhost:5000/sip/connections
```

### `POST /sip/connections`

Create a new record.

```bash
curl -X POST http://localhost:5000/sip/connections \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe"
}'
```

### `GET /sip/connections/<connection_id>`

```bash
curl http://localhost:5000/sip/connections/<connection_id>
```

### `GET /sip/health`

Health check and service status.

```bash
curl http://localhost:5000/sip/health
```

```json
{"status": "ok"}
```

### `GET /sip/failover-status`

Update record status.

```bash
curl http://localhost:5000/sip/failover-status
```

### `POST /sip/assign-number`

Assign to team member. Notifies both parties.

```bash
curl -X POST http://localhost:5000/sip/assign-number \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "connection_id": "abc-123"
}'
```

## Webhook Endpoints

### `POST /webhooks/call`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
