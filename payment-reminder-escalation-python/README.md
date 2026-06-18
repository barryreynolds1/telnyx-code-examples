# Payment Reminder Escalation

Invoice overdue: day 1 SMS, day 7 voice call with payment link, day 14 escalation to collections with full context. Integrates with Stripe/QuickBooks.

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
| `COLLECTIONS_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for collections alerts ([get it](https://api.slack.com/messaging/webhooks)) |
| `STRIPE_API_KEY` | string | `sk_...` | **yes** | Stripe secret key ([get it](https://dashboard.stripe.com/apikeys)) |

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
docker build -t payment-reminder-escalation .
docker run --env-file .env -p 5000:5000 payment-reminder-escalation
```

## API Reference

### `POST /invoices`

Create a new record.

```bash
curl -X POST http://localhost:5000/invoices \
  -H "Content-Type: application/json" \
  -d '{
  "company": "value",
  "phone": "+12125551234",
  "amount": 100,
  "due_date": "2026-07-01",
  "payment_link": "value"
}'
```

### `POST /reminders/run`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/reminders/run \
  -H "Content-Type: application/json" \
  -d '{
  "days_overdue": "1"
}'
```

### `GET /invoices`

Returns all invoices.

```bash
curl http://localhost:5000/invoices
```

### `POST /invoices/<int:idx>/paid`

Mark as paid/complete.

```bash
curl -X POST http://localhost:5000/invoices/<int:idx>/paid \
  -H "Content-Type: application/json" \
  -d '{}'
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
