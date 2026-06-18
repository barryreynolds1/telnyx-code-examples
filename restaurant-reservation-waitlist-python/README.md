# Restaurant Reservation & Waitlist

AI answers calls, checks table availability, books or adds to waitlist, texts when table is ready. Host reviews large party requests.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Answer | `POST /v2/calls/{id}/actions/answer` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Gather | `POST /v2/calls/{id}/actions/gather` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (speech)
```

## External Integrations

| Service | APIs Used |
|---------|-----------|
| Slack | Incoming Webhooks |

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → AI inference → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `HOST_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for host alerts ([get it](https://api.slack.com/messaging/webhooks)) |

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
docker build -t restaurant-reservation-waitlist .
docker run --env-file .env -p 5000:5000 restaurant-reservation-waitlist
```

## API Reference

### `POST /waitlist/add`

Create a new record.

```bash
curl -X POST http://localhost:5000/waitlist/add \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "phone": "+12125551234",
  "party_size": "2",
  "wait_minutes": "30"
}'
```

### `POST /waitlist/<int:idx>/ready`

Notify customer that service is ready.

```bash
curl -X POST http://localhost:5000/waitlist/<int:idx>/ready \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /reservations`

Returns all reservations.

```bash
curl http://localhost:5000/reservations
```

### `GET /waitlist`

Returns all waitlist.

```bash
curl http://localhost:5000/waitlist
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

Events handled: `call.initiated`, `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (speech)`

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
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
