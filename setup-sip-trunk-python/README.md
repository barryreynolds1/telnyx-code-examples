# Production-ready Flask endpoint for setting up SIP trunking via Telnyx.

Production-ready Flask endpoint for setting up SIP trunking via Telnyx.

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
docker build -t setup-sip-trunk .
docker run --env-file .env -p 5000:5000 setup-sip-trunk
```

## API Reference

### `POST /sip/setup`

```bash
curl -X POST http://localhost:5000/sip/setup \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "username": "Jane Doe",
  "password": "value"
}'
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
