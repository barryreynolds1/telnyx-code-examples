# Conference Live Poll via DTMF — host asks a question, all conference participants vote by pressing 1-4, results tallied instantly.

Conference Live Poll via DTMF — host asks a question, all conference participants vote by pressing 1-4, results tallied instantly.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control API | `POST /v2/calls` | [docs](https://developers.telnyx.com/docs/voice/call-control) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (DTMF)
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
| `CONF_NUMBER` | string | `+E.164` | **yes** | conf number |
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
docker build -t conference-live-poll-dtmf .
docker run --env-file .env -p 5000:5000 conference-live-poll-dtmf
```

## API Reference

### `POST /conference/create`

Create a new record.

```bash
curl -X POST http://localhost:5000/conference/create \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Meeting"
}'
```

### `POST /conference/<cid>/invite`

```bash
curl -X POST http://localhost:5000/conference/<cid>/invite \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "+12125551234"
}'
```

### `POST /conference/<cid>/poll`

```bash
curl -X POST http://localhost:5000/conference/<cid>/poll \
  -H "Content-Type: application/json" \
  -d '{
  "question": "value",
  "options": "value"
}'
```

### `GET /conference/<cid>/results`

```bash
curl http://localhost:5000/conference/<cid>/results
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

Events handled: `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (DTMF)`

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

- [Call Control API](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
