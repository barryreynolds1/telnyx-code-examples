# Returns Processor

Customer texts photo of defective item via MMS, AI evaluates damage, auto-approves low-value refunds via Stripe, escalates high-value to team lead.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## External Integrations

| Service | APIs Used |
|---------|-----------|
| Stripe | Checkout Sessions, Refunds, Payment Intents |
| Shopify | Orders API, Webhooks |
| Slack | Incoming Webhooks |

## How It Works

```
Inbound SMS ──► Telnyx ──► POST /webhooks/sms
                                   │
                                   ├── AI categorizes/responds
                                   ├── Takes action
                                   └── Sends reply SMS
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `STRIPE_API_KEY` | string | `sk_...` | **yes** | Stripe secret key ([get it](https://dashboard.stripe.com/apikeys)) |
| `SHOPIFY_STORE` | string | `my-store` | **yes** | Shopify store subdomain ([get it](Shopify admin)) |
| `SHOPIFY_ACCESS_TOKEN` | string | `shpat_...` | **yes** | Shopify Admin API token ([get it](Shopify admin > Apps)) |
| `SUPPORT_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for support alerts ([get it](https://api.slack.com/messaging/webhooks)) |
| `AUTO_REFUND_THRESHOLD` | integer | `50` | no | Max auto-refund amount in USD |

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

- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t returns-processor .
docker run --env-file .env -p 5000:5000 returns-processor
```

## API Reference

### `GET /returns`

Returns all returns.

```bash
curl http://localhost:5000/returns
```

### `POST /returns/<int:idx>/approve`

Approve a pending item. Sends confirmation to customer.

```bash
curl -X POST http://localhost:5000/returns/<int:idx>/approve \
  -H "Content-Type: application/json" \
  -d '{
  "agent": "unknown",
  "refund_amount": 100,
  "payment_intent": "value"
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

- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
