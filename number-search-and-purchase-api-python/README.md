# Number Search and Purchase API — search, filter, and buy phone numbers programmatically.

Number Search and Purchase API — search, filter, and buy phone numbers programmatically.

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
docker build -t number-search-and-purchase-api .
docker run --env-file .env -p 5000:5000 number-search-and-purchase-api
```

## API Reference

### `GET /numbers/search`

```bash
curl http://localhost:5000/numbers/search
```

### `POST /numbers/purchase`

```bash
curl -X POST http://localhost:5000/numbers/purchase \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "+12125551234"
}'
```

### `GET /numbers/inventory`

Returns all inventory.

```bash
curl http://localhost:5000/numbers/inventory
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
