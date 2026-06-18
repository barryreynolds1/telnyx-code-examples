# Verify Phone Number OTP Flow — Telnyx Verify API with SMS primary and voice call fallback.

Verify Phone Number OTP Flow — Telnyx Verify API with SMS primary and voice call fallback.

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → process → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `VERIFY_PROFILE_ID` | string | `-` | **yes** | verify profile id |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Webhook URL

Expose with [ngrok](https://ngrok.com): `ngrok http 5000`

Configure in [Telnyx Portal](https://portal.telnyx.com):

- **Call Control App** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/voice`

### Docker

```bash
docker build -t verify-phone-number-otp-flow .
docker run --env-file .env -p 5000:5000 verify-phone-number-otp-flow
```

## API Reference

### `POST /verify/start`

```bash
curl -X POST http://localhost:5000/verify/start \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `POST /verify/voice-fallback`

```bash
curl -X POST http://localhost:5000/verify/voice-fallback \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `POST /verify/check`

```bash
curl -X POST http://localhost:5000/verify/check \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "code": "value"
}'
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
