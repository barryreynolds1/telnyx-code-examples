# Verify Multi-Channel Auth — multi-channel verification: SMS first, fallback to voice call, then WhatsApp. Cascading 2FA.

Verify Multi-Channel Auth — multi-channel verification: SMS first, fallback to voice call, then WhatsApp. Cascading 2FA.

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
docker build -t verify-multi-channel-auth .
docker run --env-file .env -p 5000:5000 verify-multi-channel-auth
```

## API Reference

### `POST /verify/start`

```bash
curl -X POST http://localhost:5000/verify/start \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "channel": "sms",
  "timeout": "300"
}'
```

### `POST /verify/check`

```bash
curl -X POST http://localhost:5000/verify/check \
  -H "Content-Type: application/json" \
  -d '{
  "verification_id": "abc-123",
  "code": "value"
}'
```

### `POST /verify/escalate/<vid>`

```bash
curl -X POST http://localhost:5000/verify/escalate/<vid> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /verify/cascade`

```bash
curl -X POST http://localhost:5000/verify/cascade \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `GET /verifications`

Returns all verifications.

```bash
curl http://localhost:5000/verifications
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
