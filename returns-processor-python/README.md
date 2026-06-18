---
name: returns-processor
title: "Returns Processor"
description: "Customer texts photo of defective item via MMS, AI evaluates damage, auto-approves low-value refunds via Stripe, escalates high-value to team lead."
language: python
framework: flask
telnyx_products: [AI Inference]
integrations: [Stripe, Shopify, Slack]
channel: [sms]
---

# Returns Processor

Customer texts photo of defective item via MMS, AI evaluates damage, auto-approves low-value refunds via Stripe, escalates high-value to team lead.

## Telnyx API Endpoints Used

- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## External Service Integrations

- **Stripe** — Payments, refunds, checkout sessions ([docs](https://docs.stripe.com/api))
- **Shopify** — Orders, carts, product data, webhooks ([docs](https://shopify.dev/docs/api))
- **Slack** — Team notifications via incoming webhooks ([docs](https://api.slack.com/messaging/webhooks))

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│   SMS/MMS   │────►│   Telnyx   │────►│  POST /webhooks/sms  │
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
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |
| `STRIPE_API_KEY` | `string` | `sk_live_...` | **yes** | Stripe secret key | [→ link](https://dashboard.stripe.com/apikeys) |
| `SHOPIFY_STORE` | `string` | `my-store` | **yes** | Shopify store subdomain | — |
| `SHOPIFY_ACCESS_TOKEN` | `string` | `shpat_...` | **yes** | Shopify Admin API token | — |
| `SUPPORT_SLACK_WEBHOOK` | `string` | `https://hooks.slack.com/...` | no | Slack webhook for support alerts | [→ link](https://api.slack.com/messaging/webhooks) |
| `AUTO_REFUND_THRESHOLD` | `integer` | `50` | no | Max auto-refund (USD) | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/returns-processor-python
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

   - **Messaging Profile** → Inbound Webhook URL → `https://<id>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t returns-processor .
docker run --env-file .env -p 5000:5000 returns-processor
```

## API Reference

### `GET /returns`

Returns all returns.

**Request:**

```bash
curl http://localhost:5000/returns
```

**Response:**

```json
{
  "returns": [
    "..."
  ]
}
```

### `POST /returns/<int:idx>/approve`

Approves a pending item. Sends confirmation to the customer via SMS.

**Request:**

```bash
curl -X POST http://localhost:5000/returns/0/approve \
  -H "Content-Type: application/json" \
  -d '{
  "agent": "unknown",
  "refund_amount": 150.0,
  "payment_intent": "pi_abc123"
}'
```

**Response:**

```json
{
  "return": "..."
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

### `POST /webhooks/sms`

Receives [Telnyx Messaging](https://developers.telnyx.com/docs/messaging) webhook events.

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "message.received",
    "direction": "inbound",
    "payload": {
      "id": "f5d7a7e0-1234-5678-9abc-def012345678",
      "from": {
        "phone_number": "+12125551234",
        "carrier": "Verizon",
        "line_type": "Wireless"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "HELP",
      "type": "SMS",
      "media": [],
      "received_at": "2026-07-15T14:30:00Z"
    }
  }
}
```

## Resources

- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
- [Stripe Documentation](https://docs.stripe.com/api)
- [Shopify Documentation](https://shopify.dev/docs/api)
- [Slack Documentation](https://api.slack.com/messaging/webhooks)
