---
name: patient-appointment-engine
title: "Patient Appointment Engine"
description: "AI answers calls, checks availability, books appointments, collects copay via Stripe, sends SMS confirmation. Staff reviews next-day schedule."
language: python
framework: flask
telnyx_products: [Voice, AI Inference]
integrations: [Stripe, Slack]
channel: [voice]
---

# Patient Appointment Engine

AI answers calls, checks availability, books appointments, collects copay via Stripe, sends SMS confirmation. Staff reviews next-day schedule.

## Telnyx API Endpoints Used

- **Call Control: Answer**: `POST /v2/calls/{call_control_id}/actions/answer` — [API reference](https://developers.telnyx.com/api/call-control/answer-call)
- **Call Control: Speak (TTS)**: `POST /v2/calls/{call_control_id}/actions/speak` — [API reference](https://developers.telnyx.com/api/call-control/speak)
- **Call Control: Gather (STT/DTMF)**: `POST /v2/calls/{call_control_id}/actions/gather_using_speak` — [API reference](https://developers.telnyx.com/api/call-control/gather)
- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers
- `call.answered` — call connected, app speaks greeting
- `call.speak.ended` — TTS finished, app starts listening
- `call.gather.ended` — caller input received (speech or DTMF)
- `call.hangup` — call ended, app cleans up session

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
                                          │ Telnyx Inference │
                                          │ (AI processing) │
                                          └────────┬────────┘
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
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |
| `STRIPE_API_KEY` | `string` | `sk_live_...` | **yes** | Stripe secret key | [→ link](https://dashboard.stripe.com/apikeys) |
| `STAFF_SLACK_WEBHOOK` | `string` | `https://hooks.slack.com/...` | no | Slack webhook for staff alerts | [→ link](https://api.slack.com/messaging/webhooks) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/patient-appointment-engine-python
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
docker build -t patient-appointment-engine .
docker run --env-file .env -p 5000:5000 patient-appointment-engine
```

## API Reference

### `GET /appointments`

Returns all appointments.

**Request:**

```bash
curl http://localhost:5000/appointments
```

**Response:**

```json
{
  "appointments": "...",
  "pending_review": "..."
}
```

### `POST /appointments/<int:idx>/approve`

Approves a pending item. Sends confirmation to the customer via SMS.

**Request:**

```bash
curl -X POST http://localhost:5000/appointments/0/approve
```

**Response:**

```json
{
  "appointment": "..."
}
```

### `POST /appointments/<int:idx>/reject`

Rejects a pending item. Sends notification to the customer via SMS.

**Request:**

```bash
curl -X POST http://localhost:5000/appointments/0/reject \
  -H "Content-Type: application/json" \
  -d '{
  "reason": "Outside practice area"
}'
```

**Response:**

```json
{
  "appointment": "..."
}
```

### `POST /copay/create`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/copay/create \
  -H "Content-Type: application/json" \
  -d '{
  "amount_cents": 2500
}'
```

**Response:**

```json
{
  "payment_link": "..."
}
```

### `GET /slots`

Returns slots details.

**Request:**

```bash
curl http://localhost:5000/slots
```

**Response:**

```json
{
  "available": "..."
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

**Events handled:** `call.initiated`, `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`

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

- [Call Control: Answer — API Reference](https://developers.telnyx.com/api/call-control/answer-call)
- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
- [Stripe Documentation](https://docs.stripe.com/api)
- [Slack Documentation](https://api.slack.com/messaging/webhooks)
