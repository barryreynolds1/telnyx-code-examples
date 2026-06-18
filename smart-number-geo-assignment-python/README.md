# Smart Number Geo-Assignment — automatically purchase and assign local numbers based on caller geography to maximize answer rates.

Smart Number Geo-Assignment — automatically purchase and assign local numbers based on caller geography to maximize answer rates.

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
docker build -t smart-number-geo-assignment .
docker run --env-file .env -p 5000:5000 smart-number-geo-assignment
```

## API Reference

### `POST /assign`

Assign to team member. Notifies both parties.

```bash
curl -X POST http://localhost:5000/assign \
  -H "Content-Type: application/json" \
  -d '{
  "area_code": "value",
  "use_case": "outbound"
}'
```

### `POST /lookup-and-assign`

Assign to team member. Notifies both parties.

```bash
curl -X POST http://localhost:5000/lookup-and-assign \
  -H "Content-Type: application/json" \
  -d '{
  "target_number": "+12125551234"
}'
```

### `GET /inventory`

```bash
curl http://localhost:5000/inventory
```

### `GET /assignments`

Returns all assignments.

```bash
curl http://localhost:5000/assignments
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
