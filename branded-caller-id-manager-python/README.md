# Branded Caller ID Manager — register, manage, and verify branded calling profiles with STIR/SHAKEN attestation for higher answer rates.

Branded Caller ID Manager — register, manage, and verify branded calling profiles with STIR/SHAKEN attestation for higher answer rates.

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
docker build -t branded-caller-id-manager .
docker run --env-file .env -p 5000:5000 branded-caller-id-manager
```

## API Reference

### `POST /brands`

Create a new record.

```bash
curl -X POST http://localhost:5000/brands \
  -H "Content-Type: application/json" \
  -d '{
  "entity_type": "PRIVATE_PROFIT",
  "display_name": "Jane Doe",
  "company_name": "Jane Doe",
  "ein": "value",
  "phone": "+12125551234",
  "street": "value",
  "city": "value",
  "state": "value",
  "postal_code": "value",
  "country": "US",
  "vertical": "TECHNOLOGY",
  "website": "value"
}'
```

### `GET /brands`

Returns all brands.

```bash
curl http://localhost:5000/brands
```

### `POST /campaigns`

Create a new record.

```bash
curl -X POST http://localhost:5000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
  "brand_id": "abc-123",
  "usecase": "MIXED",
  "description": "value",
  "sample_message": "[\"Your appointment is tomorrow at 2pm. Reply CONFIRM.\"]",
  "phone_numbers": "+12125551234"
}'
```

### `PUT /numbers/<number>/caller-id`

Update record status.

```bash
curl -X PUT http://localhost:5000/numbers/<number>/caller-id \
  -H "Content-Type: application/json" \
  -d '{
  "business_name": "Jane Doe"
}'
```

### `GET /stir-shaken/status`

Update record status.

```bash
curl http://localhost:5000/stir-shaken/status
```

### `GET /campaigns`

Returns all campaigns.

```bash
curl http://localhost:5000/campaigns
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
