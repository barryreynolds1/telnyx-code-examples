# Law Firm Client Intake

AI answers after-hours calls, screens case type, collects facts, runs conflict check, books consultation via Calendly, collects retainer deposit via Stripe.

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
| Stripe | Checkout Sessions, Refunds, Payment Intents |
| Calendly | Scheduling Links |
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
| `STRIPE_API_KEY` | string | `sk_...` | **yes** | Stripe secret key ([get it](https://dashboard.stripe.com/apikeys)) |
| `CALENDLY_TOKEN` | string | `token` | no | Calendly personal access token ([get it](https://calendly.com/integrations/api_webhooks)) |
| `ATTORNEY_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for attorney alerts ([get it](https://api.slack.com/messaging/webhooks)) |

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
docker build -t law-firm-client-intake .
docker run --env-file .env -p 5000:5000 law-firm-client-intake
```

## API Reference

### `GET /intakes`

Returns all intakes.

```bash
curl http://localhost:5000/intakes
```

### `POST /intakes/<int:idx>/accept`

Accept and schedule. Sends confirmation.

```bash
curl -X POST http://localhost:5000/intakes/<int:idx>/accept \
  -H "Content-Type: application/json" \
  -d '{
  "attorney": "value",
  "time": "09:00"
}'
```

### `POST /intakes/<int:idx>/decline`

Deny/reject a pending item. Notifies customer.

```bash
curl -X POST http://localhost:5000/intakes/<int:idx>/decline \
  -H "Content-Type: application/json" \
  -d '{
  "reason": "value"
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

## Resources

- [Call Control: Answer](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
