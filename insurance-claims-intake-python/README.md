# Insurance Claims Intake

Policyholder calls, AI collects incident details, accepts photos via MMS, creates claim, assigns adjuster, texts status updates. Adjuster reviews AI-prepared claim.

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
Inbound Call/SMS ──► Telnyx ──► POST /webhooks/voice or /webhooks/sms
                                        │
                                        ├── Telnyx AI Inference
                                        ├── Slack
                                        │
                                        ▼
                                  Response / Action
                                  (speak, SMS, dispatch)
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `ADJUSTER_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for adjuster alerts ([get it](https://api.slack.com/messaging/webhooks)) |

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
- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t insurance-claims-intake .
docker run --env-file .env -p 5000:5000 insurance-claims-intake
```

## API Reference

### `GET /claims`

Returns all claims.

```bash
curl http://localhost:5000/claims
```

### `POST /claims/<claim_id>/assign`

Assign to team member. Notifies both parties.

```bash
curl -X POST http://localhost:5000/claims/<claim_id>/assign \
  -H "Content-Type: application/json" \
  -d '{
  "adjuster": "value"
}'
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

### `POST /webhooks/sms`

Receives Telnyx Messaging webhook events.

Example payload:

```json
{
  "data": {
    "event_type": "message.received",
    "payload": {
      "from": {
        "phone_number": "+12125551234"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "Hello",
      "media": []
    }
  }
}
```

## Resources

- [Call Control: Answer](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
