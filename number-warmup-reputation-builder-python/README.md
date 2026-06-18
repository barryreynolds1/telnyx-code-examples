# Number Warmup & Reputation Builder — gradually ramp SMS volume on new numbers to build carrier reputation and avoid spam flags.

Number Warmup & Reputation Builder — gradually ramp SMS volume on new numbers to build carrier reputation and avoid spam flags.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `MESSAGING_PROFILE_ID` | string | `uuid` | no | Telnyx messaging profile ID ([get it](https://portal.telnyx.com/messaging/profiles)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t number-warmup-reputation-builder .
docker run --env-file .env -p 5000:5000 number-warmup-reputation-builder
```

## API Reference

### `POST /warmup/start`

```bash
curl -X POST http://localhost:5000/warmup/start \
  -H "Content-Type: application/json" \
  -d '{
  "number": "+12125551234"
}'
```

### `POST /warmup/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/warmup/send \
  -H "Content-Type: application/json" \
  -d '{
  "from_number": "+12125551234",
  "text": "Test message for number warmup"
}'
```

### `GET /warmup/status`

Update record status.

```bash
curl http://localhost:5000/warmup/status
```

### `POST /warmup/reset-daily`

```bash
curl -X POST http://localhost:5000/warmup/reset-daily \
  -H "Content-Type: application/json" \
  -d '{}'
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

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
