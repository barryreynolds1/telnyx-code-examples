# Flask application for managing inbound SIP routing with Telnyx.

Flask application for managing inbound SIP routing with Telnyx.

## Webhook Events Handled

```
call.gather.ended (DTMF)
```

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
docker build -t inbound-sip-routing .
docker run --env-file .env -p 5000:5000 inbound-sip-routing
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
  "name": "Jane Doe",
  "sip_uri": "value",
  "username": "Jane Doe",
  "password": "value"
}'
```

### `GET /sip/connections/<connection_id>`

```bash
curl http://localhost:5000/sip/connections/<connection_id>
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
