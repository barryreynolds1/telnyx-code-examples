# Bulk Number Validation & Cleaner — validate and clean phone number lists via Telnyx Number Lookup API.

Bulk Number Validation & Cleaner — validate and clean phone number lists via Telnyx Number Lookup API.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Number Lookup API | `GET /v2/number_lookup/{number}` | [docs](https://developers.telnyx.com/docs/numbers) |

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
docker build -t bulk-number-validation-cleaner .
docker run --env-file .env -p 5000:5000 bulk-number-validation-cleaner
```

## API Reference

### `POST /validate`

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "+12125551234"
}'
```

### `GET /validate/single/<number>`

```bash
curl http://localhost:5000/validate/single/<number>
```

### `GET /jobs`

Returns all jobs.

```bash
curl http://localhost:5000/jobs
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

- [Number Lookup API](https://developers.telnyx.com/docs/numbers)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
