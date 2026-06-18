---
name: law-firm-client-intake
title: "Law Firm Client Intake"
description: "AI answers after-hours calls, screens case type, collects facts, runs conflict check, books consultation via Calendly, collects retainer deposit via Stripe."
language: python
framework: flask
telnyx_products: [Voice, AI Inference]
integrations: [Stripe, Calendly, Slack]
channel: [voice]
---

# Law Firm Client Intake

AI answers after-hours calls, screens case type, collects facts, runs conflict check, books consultation via Calendly, collects retainer deposit via Stripe.

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
- **Calendly** — Appointment scheduling links ([docs](https://developer.calendly.com))
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
                                          │ Calendly         │
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
| `CALENDLY_TOKEN` | `string` | `...` | no | Calendly personal access token | — |
| `ATTORNEY_SLACK_WEBHOOK` | `string` | `https://hooks.slack.com/...` | no | Slack webhook for attorney alerts | [→ link](https://api.slack.com/messaging/webhooks) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/law-firm-client-intake-python
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
docker build -t law-firm-client-intake .
docker run --env-file .env -p 5000:5000 law-firm-client-intake
```

## API Reference

### `GET /intakes`

Returns all intakes.

**Request:**

```bash
curl http://localhost:5000/intakes
```

**Response:**

```json
{
  "intakes": "..."
}
```

### `POST /intakes/<int:idx>/accept`

Accepts and schedules. Sends confirmation via SMS.

**Request:**

```bash
curl -X POST http://localhost:5000/intakes/0/accept \
  -H "Content-Type: application/json" \
  -d '{
  "attorney": "Sarah Chen",
  "time": "14:00"
}'
```

**Response:**

```json
{
  "intake": "..."
}
```

### `POST /intakes/<int:idx>/decline`

Declines a pending item. Sends notification to the customer via SMS.

**Request:**

```bash
curl -X POST http://localhost:5000/intakes/0/decline \
  -H "Content-Type: application/json" \
  -d '{
  "reason": "Outside practice area"
}'
```

**Response:**

```json
{
  "intake": "..."
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
- [Calendly Documentation](https://developer.calendly.com)
- [Slack Documentation](https://api.slack.com/messaging/webhooks)
