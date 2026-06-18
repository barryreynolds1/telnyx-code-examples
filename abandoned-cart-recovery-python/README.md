---
name: abandoned-cart-recovery
title: "Abandoned Cart Recovery"
description: "SMS 1h after abandon with incentive, AI voice call 24h later if no purchase. Integrates with Shopify webhooks and Stripe for discount codes."
language: python
framework: flask
telnyx_products: [Voice, AI Inference]
integrations: [Stripe, Shopify]
channel: [voice, sms]
---

# Abandoned Cart Recovery

SMS 1h after abandon with incentive, AI voice call 24h later if no purchase. Integrates with Shopify webhooks and Stripe for discount codes.

## Telnyx API Endpoints Used

- **Call Control: Speak (TTS)**: `POST /v2/calls/{call_control_id}/actions/speak` — [API reference](https://developers.telnyx.com/api/call-control/speak)
- **Call Control: Gather (STT/DTMF)**: `POST /v2/calls/{call_control_id}/actions/gather_using_speak` — [API reference](https://developers.telnyx.com/api/call-control/gather)
- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.answered` — call connected, app speaks greeting
- `call.speak.ended` — TTS finished, app starts listening
- `call.gather.ended` — caller input received (speech or DTMF)

## External Service Integrations

- **Stripe** — Payments, refunds, checkout sessions ([docs](https://docs.stripe.com/api))
- **Shopify** — Orders, carts, product data, webhooks ([docs](https://shopify.dev/docs/api))

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│  Phone Call  │────►│            │────►│  POST /webhooks/voice│
│  or SMS/MMS  │     │   Telnyx   │     │  POST /webhooks/sms  │
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
                                          │ Shopify          │
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
| `SHOPIFY_STORE` | `string` | `my-store` | **yes** | Shopify store subdomain | — |
| `SHOPIFY_ACCESS_TOKEN` | `string` | `shpat_...` | **yes** | Shopify Admin API token | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/abandoned-cart-recovery-python
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
   - **Messaging Profile** → Inbound Webhook URL → `https://<id>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t abandoned-cart-recovery .
docker run --env-file .env -p 5000:5000 abandoned-cart-recovery
```

## API Reference

### `POST /recovery/run-sms`

Executes the batch workflow.

**Request:**

```bash
curl -X POST http://localhost:5000/recovery/run-sms
```

**Response:**

```json
{
  "results": "..."
}
```

### `POST /recovery/run-calls`

Executes the batch workflow.

**Request:**

```bash
curl -X POST http://localhost:5000/recovery/run-calls
```

**Response:**

```json
{
  "results": "..."
}
```

### `GET /carts`

Returns all carts.

**Request:**

```bash
curl http://localhost:5000/carts
```

**Response:**

```json
{
  "carts": [
    "..."
  ]
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

### `POST /webhooks/shopify/cart-abandoned`

Receives [Shopify webhook](https://shopify.dev/docs/api/webhooks) events.

### `POST /webhooks/voice`

Receives [Telnyx Call Control](https://developers.telnyx.com/docs/voice/call-control) webhook events.

**Events handled:** `call.answered`, `call.speak.ended`, `call.gather.ended`

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

### `POST /webhooks/shopify/order-created`

Receives [Shopify webhook](https://shopify.dev/docs/api/webhooks) events.

## Resources

- [Call Control: Speak (TTS) — API Reference](https://developers.telnyx.com/api/call-control/speak)
- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
- [Stripe Documentation](https://docs.stripe.com/api)
- [Shopify Documentation](https://shopify.dev/docs/api)
