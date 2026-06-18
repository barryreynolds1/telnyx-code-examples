# Porting LOA Automation — automate Letter of Authorization generation and porting order submission.

Porting LOA Automation — automate Letter of Authorization generation and porting order submission.

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
docker build -t porting-loa-automation .
docker run --env-file .env -p 5000:5000 porting-loa-automation
```

## API Reference

### `POST /loa/generate`

```bash
curl -X POST http://localhost:5000/loa/generate \
  -H "Content-Type: application/json" \
  -d '{
  "authorized_person": "value",
  "current_provider": "abc-123",
  "phone_numbers": "+12125551234",
  "billing_number": "+12125551234",
  "account_number": "+12125551234",
  "service_address": "value",
  "title": "value",
  "company": "value"
}'
```

### `POST /loa/submit-and-port`

```bash
curl -X POST http://localhost:5000/loa/submit-and-port \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "+12125551234",
  "authorized_person": "value",
  "current_provider": "abc-123",
  "billing_number": "+12125551234"
}'
```

### `POST /loa/check-portability`

```bash
curl -X POST http://localhost:5000/loa/check-portability \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "+12125551234"
}'
```

### `GET /loa`

Returns all loas.

```bash
curl http://localhost:5000/loa
```

### `GET /pipeline`

Update record status.

```bash
curl http://localhost:5000/pipeline
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
