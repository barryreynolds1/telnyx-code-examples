# Production-ready OTP 2FA system with Flask and Telnyx SMS.

Production-ready OTP 2FA system with Flask and Telnyx SMS.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Cloud Storage API | `S3-compatible` | [docs](https://developers.telnyx.com/docs/storage) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `OTP_EXPIRY_SECONDS` | string | `-` | no | otp expiry seconds |
| `TELNYX_PHONE_NUMBER` | string | `+E.164` | **yes** | telnyx phone number |
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
docker build -t sms-two-factor-auth .
docker run --env-file .env -p 5000:5000 sms-two-factor-auth
```

## API Reference

### `POST /auth/request-otp`

```bash
curl -X POST http://localhost:5000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `POST /auth/verify-otp`

```bash
curl -X POST http://localhost:5000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234",
  "code": "value"
}'
```

### `GET /auth/otp-status`

Update record status.

```bash
curl http://localhost:5000/auth/otp-status
```

## Resources

- [Cloud Storage API](https://developers.telnyx.com/docs/storage)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
