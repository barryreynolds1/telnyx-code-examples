---
name: payment-reminder-escalation
title: "Payment Reminder Escalation"
description: "Invoice overdue: day 1 SMS, day 7 voice call with payment link, day 14 escalation to collections with full context. Integrates with Stripe/QuickBooks."
language: python
framework: flask
telnyx_products: [Voice]
integrations: [Stripe, Slack]
channel: [voice]
---

# Payment Reminder Escalation

Invoice overdue: day 1 SMS, day 7 voice call with payment link, day 14 escalation to collections with full context. Integrates with Stripe/QuickBooks.

## Telnyx API Endpoints Used

- **Call Control: Speak (TTS)**: `POST /v2/calls/{call_control_id}/actions/speak` — [API reference](https://developers.telnyx.com/api/call-control/speak)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.answered` — call connected, app speaks greeting

## External Service Integrations

- **Stripe** — Payments, refunds, checkout sessions ([docs](https://docs.stripe.com/api))
- **Slack** — Team notifications via incoming webhooks ([docs](https://api.slack.com/messaging/webhooks))

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│  Phone Call  │────►│   Telnyx   │────►│  POST /webhooks/voice│
└─────────────┘     │   Cloud    │     └──────────┬───────────┘
                    └────────────┘                │
                                                   │
                                          ┌────────┴────────┐
                                          │ Stripe           │
                                          ├─────────────────┤
                                          │ Slack            │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Response (SMS/  │
                                          │ Voice/Webhook)  │
                                          └─────────────────┘
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Type | Example | Required | Description | Where to get it |
|----------|------|---------|----------|-------------|-----------------|
| `TELNYX_API_KEY` | `string` | `KEY...` | **yes** | Telnyx API v2 key | [→ link](https://portal.telnyx.com/api-keys) |
| `MAIN_NUMBER` | `string` | `+18005551234` | **yes** | Telnyx phone number (E.164) | [→ link](https://portal.telnyx.com/numbers/my-numbers) |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |
| `COLLECTIONS_SLACK_WEBHOOK` | `string` | `https://hooks.slack.com/...` | no | Slack webhook for collections alerts | [→ link](https://api.slack.com/messaging/webhooks) |
| `STRIPE_API_KEY` | `string` | `sk_live_...` | **yes** | Stripe secret key | [→ link](https://dashboard.stripe.com/apikeys) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/payment-reminder-escalation-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Webhook Configuration

1. Expose your local server:

   ```bash
   ngrok http 5000
   ```

2. Copy the HTTPS URL and configure in [Telnyx Portal](https://portal.telnyx.com):

   - **Call Control Application** → Webhook URL → `https://<id>.ngrok.io/webhooks/voice`

### Docker

```bash
docker build -t payment-reminder-escalation .
docker run --env-file .env -p 5000:5000 payment-reminder-escalation
```

## API Reference

### `POST /invoices`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/invoices \
  -H "Content-Type: application/json" \
  -d '{
  "company": "Acme Corp",
  "phone": "+12125551234",
  "amount": 150.0,
  "due_date": "2026-07-15",
  "payment_link": "https://pay.example.com/inv-123"
}'
```

**Response:**

```json
{
  "invoice": "..."
}
```

### `POST /reminders/run`

Executes the batch workflow.

**Request:**

```bash
curl -X POST http://localhost:5000/reminders/run \
  -H "Content-Type: application/json" \
  -d '{
  "days_overdue": 1
}'
```

**Response:**

```json
{
  "results": "..."
}
```

### `GET /invoices`

Returns all invoices.

**Request:**

```bash
curl http://localhost:5000/invoices
```

**Response:**

```json
{
  "invoices": "..."
}
```

### `POST /invoices/<int:idx>/paid`

Updates the record status.

**Request:**

```bash
curl -X POST http://localhost:5000/invoices/0/paid
```

**Response:**

```json
{
  "invoice": "..."
}
```

### `GET /health`

Returns service health and operational metrics.

**Request:**

```bash
curl http://localhost:5000/health
```

**Response:**

```json
{
  "status": "ok"
}
```

## Webhook Endpoints

### `POST /webhooks/voice`

Receives [Telnyx Call Control](https://developers.telnyx.com/docs/voice/call-control) webhook events.

**Events handled:** `call.answered`

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:uMi2qMWHT-mLFGkEm4t9tA",
    "connection_id": "1494404757140276705",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876",
    "call_leg_id": "428c31b6-7af4-4bcb-b7f5-5013ef9657c1",
    "client_state": null,
    "state": "ringing"
  },
  "meta": {
    "attempt": 1,
    "delivered_to": "https://your-server.example.com/webhooks/voice"
  }
}
```

## Resources

- [Call Control: Speak (TTS) — API Reference](https://developers.telnyx.com/api/call-control/speak)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
- [Stripe Documentation](https://docs.stripe.com/api)
- [Slack Documentation](https://api.slack.com/messaging/webhooks)
