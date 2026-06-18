# Call Queue with Hold Music — queue callers with position announcements and hold music, route to agents.

Call Queue with Hold Music — queue callers with position announcements and hold music, route to agents.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Cloud Storage API | `S3-compatible` | [docs](https://developers.telnyx.com/docs/storage) |

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
| `QUEUE_NUMBER` | string | `+E.164` | **yes** | queue number |
| `AGENT_NUMBERS` | string | `+E.164` | **yes** | agent numbers |
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
docker build -t call-queue-with-hold-music .
docker run --env-file .env -p 5000:5000 call-queue-with-hold-music
```

## API Reference

### `GET /queue`

Update record status.

```bash
curl http://localhost:5000/queue
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

- [Cloud Storage API](https://developers.telnyx.com/docs/storage)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
