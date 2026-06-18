# Production-ready WebRTC calling application with Telnyx Voice API and FastAPI.

Production-ready WebRTC calling application with Telnyx Voice API and FastAPI.

## Webhook Events Handled

```
call.initiated
call.answered
call.hangup
call.gather.ended (DTMF)
```

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `TELNYX_PHONE_NUMBER` | string | `+E.164` | **yes** | telnyx phone number |
| `TELNYX_CONNECTION_ID` | string | `-` | **yes** | telnyx connection id |
| `WEBHOOK_URL` | string | `https://...` | **yes** | webhook url |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t webrtc-browser-calling .
docker run --env-file .env -p 5000:5000 webrtc-browser-calling
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
