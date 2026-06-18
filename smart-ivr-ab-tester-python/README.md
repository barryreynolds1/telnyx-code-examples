# Smart IVR A/B Tester — run two IVR flows simultaneously and track which converts better.

Smart IVR A/B Tester — run two IVR flows simultaneously and track which converts better.

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (DTMF)
call.gather.ended (speech)
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
| `IVR_NUMBER` | string | `+E.164` | **yes** | ivr number |
| `AGENT_NUMBER` | string | `+E.164` | **yes** | agent number |

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
docker build -t smart-ivr-ab-tester .
docker run --env-file .env -p 5000:5000 smart-ivr-ab-tester
```

## API Reference

### `POST /experiments`

Create a new record.

```bash
curl -X POST http://localhost:5000/experiments \
  -H "Content-Type: application/json" \
  -d '{
  "variant_a": "value",
  "variant_b": "value",
  "split": "0.5"
}'
```

### `GET /experiments/<eid>/results`

```bash
curl http://localhost:5000/experiments/<eid>/results
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

Events handled: `call.initiated`, `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (DTMF)`, `call.gather.ended (speech)`

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

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
