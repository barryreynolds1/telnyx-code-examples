# TeXML Dynamic Call Router — time-of-day and caller-based routing with TeXML responses.

TeXML Dynamic Call Router — time-of-day and caller-based routing with TeXML responses.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `BUSINESS_HOURS_NUMBER` | string | `+E.164` | no | business hours number |
| `AFTER_HOURS_NUMBER` | string | `+E.164` | no | after hours number |
| `VOICEMAIL_URL` | string | `https://...` | no | voicemail url |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t texml-dynamic-call-router .
docker run --env-file .env -p 5000:5000 texml-dynamic-call-router
```

## API Reference

### `POST /texml/route`

```bash
curl -X POST http://localhost:5000/texml/route \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /texml/recording`

```bash
curl -X POST http://localhost:5000/texml/recording \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /vip`

Create a new record.

```bash
curl -X POST http://localhost:5000/vip \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "name": "Jane Doe"
}'
```

### `GET /calls`

Returns all calls.

```bash
curl http://localhost:5000/calls
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
