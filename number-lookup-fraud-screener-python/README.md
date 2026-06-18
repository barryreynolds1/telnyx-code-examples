# Number Lookup Fraud Screener — screen inbound calls/messages for fraud indicators using number lookup before connecting.

Number Lookup Fraud Screener — screen inbound calls/messages for fraud indicators using number lookup before connecting.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Number Lookup API | `GET /v2/number_lookup/{number}` | [docs](https://developers.telnyx.com/docs/numbers) |

## Webhook Events Handled

```
call.initiated
```

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
docker build -t number-lookup-fraud-screener .
docker run --env-file .env -p 5000:5000 number-lookup-fraud-screener
```

## API Reference

### `GET /screen/<number>`

```bash
curl http://localhost:5000/screen/<number>
```

### `POST /blocklist`

Create a new record.

```bash
curl -X POST http://localhost:5000/blocklist \
  -H "Content-Type: application/json" \
  -d '{
  "number": "+12125551234"
}'
```

### `GET /blocklist`

Returns all blocklist.

```bash
curl http://localhost:5000/blocklist
```

### `GET /screening-log`

```bash
curl http://localhost:5000/screening-log
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Webhook Endpoints

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.initiated`

Example payload:

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:abc-123",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876"
  }
}
```

## Resources

- [Number Lookup API](https://developers.telnyx.com/docs/numbers)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
