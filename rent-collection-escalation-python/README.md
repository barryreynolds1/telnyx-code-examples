# Rent Collection Escalation

Automated multi-channel rent reminders. Day 1: SMS + Stripe payment link. Day 3: voice call. Day 7: late fee notice. Day 14: manager escalation.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |

## Webhook Events Handled

```
call.answered
```

## External Integrations

| Service | APIs Used |
|---------|-----------|
| Stripe | Checkout Sessions, Refunds, Payment Intents |
| Slack | Incoming Webhooks |

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
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `STRIPE_API_KEY` | string | `sk_...` | **yes** | Stripe secret key ([get it](https://dashboard.stripe.com/apikeys)) |
| `MANAGER_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for manager alerts ([get it](https://api.slack.com/messaging/webhooks)) |

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
docker build -t rent-collection-escalation .
docker run --env-file .env -p 5000:5000 rent-collection-escalation
```

## API Reference

### `POST /collections/run`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/collections/run \
  -H "Content-Type: application/json" \
  -d '{
  "day_overdue": "1"
}'
```

### `GET /tenants`

Returns all tenants.

```bash
curl http://localhost:5000/tenants
```

### `PUT /tenants/<int:idx>/status`

Update record status.

```bash
curl -X PUT http://localhost:5000/tenants/<int:idx>/status \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /collections/log`

```bash
curl http://localhost:5000/collections/log
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

Events handled: `call.answered`

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

- [Call Control: Speak](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
