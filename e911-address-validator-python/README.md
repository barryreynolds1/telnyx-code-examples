# E911 Address Validator — validate and provision E911 addresses via API.

E911 Address Validator — validate and provision E911 addresses via API.

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
docker build -t e911-address-validator .
docker run --env-file .env -p 5000:5000 e911-address-validator
```

## API Reference

### `POST /e911/validate`

Create a new record.

```bash
curl -X POST http://localhost:5000/e911/validate \
  -H "Content-Type: application/json" \
  -d '{
  "street": "value",
  "street2": "value",
  "city": "value",
  "state": "value",
  "zip": "value",
  "country": "US",
  "business_name": "Jane Doe"
}'
```

### `POST /e911/assign`

Assign to team member. Notifies both parties.

```bash
curl -X POST http://localhost:5000/e911/assign \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "address_id": "abc-123"
}'
```

### `GET /e911/addresses`

Returns all addresses.

```bash
curl http://localhost:5000/e911/addresses
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
