# Multi-Number Identity Router — route calls based on which number was dialed. Each number maps to a different business identity, greeting, and routing destination.

Multi-Number Identity Router — route calls based on which number was dialed. Each number maps to a different business identity, greeting, and routing destination.

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.hangup
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
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |

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
docker build -t multi-number-identity-router .
docker run --env-file .env -p 5000:5000 multi-number-identity-router
```

## API Reference

### `POST /identities`

Create a new record.

```bash
curl -X POST http://localhost:5000/identities \
  -H "Content-Type: application/json" \
  -d '{
  "number": "+12125551234",
  "name": "Jane Doe",
  "greeting": "value",
  "forward_to": "value",
  "hours": "24/7"
}'
```

### `GET /identities`

Returns all identities.

```bash
curl http://localhost:5000/identities
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

## Webhook Endpoints

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.initiated`, `call.answered`, `call.speak.ended`, `call.hangup`

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
