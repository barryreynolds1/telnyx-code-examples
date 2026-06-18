# Abandoned Cart Recovery

SMS 1h after abandon with incentive, AI voice call 24h later if no purchase. Integrates with Shopify webhooks and Stripe for discount codes.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Gather | `POST /v2/calls/{id}/actions/gather` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.gather.ended
call.gather.ended (speech)
```

## External Integrations

| Service | APIs Used |
|---------|-----------|
| Stripe | Checkout Sessions, Refunds, Payment Intents |
| Shopify | Orders API, Webhooks |

## How It Works

```
Inbound Call/SMS ──► Telnyx ──► POST /webhooks/voice or /webhooks/sms
                                        │
                                        ├── Telnyx AI Inference
                                        ├── Stripe
                                        ├── Shopify
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
| `SHOPIFY_STORE` | string | `my-store` | **yes** | Shopify store subdomain ([get it](Shopify admin)) |
| `SHOPIFY_ACCESS_TOKEN` | string | `shpat_...` | **yes** | Shopify Admin API token ([get it](Shopify admin > Apps)) |

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
docker build -t abandoned-cart-recovery .
docker run --env-file .env -p 5000:5000 abandoned-cart-recovery
```

## API Reference

### `POST /recovery/run-sms`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/recovery/run-sms \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /recovery/run-calls`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/recovery/run-calls \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /carts`

Returns all carts.

```bash
curl http://localhost:5000/carts
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

### `POST /webhooks/shopify/cart-abandoned`

Receives Shopify webhook events.

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.gather.ended (speech)`

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

### `POST /webhooks/shopify/order-created`

Receives Shopify webhook events.

## Resources

- [Call Control: Speak](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
