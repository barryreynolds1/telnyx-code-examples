# Media Stream Voice Cloak — real-time voice modification via media streaming API. Apply pitch shift, echo, or anonymization.

Media Stream Voice Cloak — real-time voice modification via media streaming API. Apply pitch shift, echo, or anonymization.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Answer | `POST /v2/calls/{id}/actions/answer` | [docs](https://developers.telnyx.com/docs/voice/call-control) |

## Webhook Events Handled

```
call.initiated
call.answered
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
| `STREAM_WEBSOCKET_URL` | string | `https://...` | no | stream websocket url |

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
docker build -t media-stream-voice-cloak .
docker run --env-file .env -p 5000:5000 media-stream-voice-cloak
```

## API Reference

### `POST /cloak/<ccid>`

```bash
curl -X POST http://localhost:5000/cloak/<ccid> \
  -H "Content-Type: application/json" \
  -d '{
  "effect": "anonymous"
}'
```

### `GET /effects`

Returns all effects.

```bash
curl http://localhost:5000/effects
```

### `GET /active`

Returns all active.

```bash
curl http://localhost:5000/active
```

### `GET /log`

```bash
curl http://localhost:5000/log
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

Events handled: `call.initiated`, `call.answered`, `call.hangup`

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

- [Call Control: Answer](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
