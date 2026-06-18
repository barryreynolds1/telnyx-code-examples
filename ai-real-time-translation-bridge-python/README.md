# AI Real-Time Translation Bridge — connect two callers who speak different languages.
AI translates each side's speech before playing it to the other party.

AI Real-Time Translation Bridge — connect two callers who speak different languages.
AI translates each side's speech before playing it to the other party.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control API | `POST /v2/calls` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Hangup | `POST /v2/calls/{id}/actions/hangup` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (speech)
```

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
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `BRIDGE_NUMBER` | string | `+E.164` | **yes** | bridge number |
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
docker build -t ai-real-time-translation-bridge .
docker run --env-file .env -p 5000:5000 ai-real-time-translation-bridge
```

## API Reference

### `POST /bridge`

Create a new record.

```bash
curl -X POST http://localhost:5000/bridge \
  -H "Content-Type: application/json" \
  -d '{
  "number_a": "+12125551234",
  "lang_a": "English",
  "number_b": "+12125551234",
  "lang_b": "Spanish"
}'
```

### `GET /bridges`

Returns all bridges.

```bash
curl http://localhost:5000/bridges
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

Events handled: `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (speech)`

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
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
