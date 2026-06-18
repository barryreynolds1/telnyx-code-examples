# x402 USDC Account Funder — fund your Telnyx account with USDC cryptocurrency on the Base blockchain.

X402 USDC Account Funder — fund your Telnyx account with USDC cryptocurrency on the Base blockchain.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t x402-usdc-account-funder .
docker run --env-file .env -p 5000:5000 x402-usdc-account-funder
```

## API Reference

### `POST /quote`

```bash
curl -X POST http://localhost:5000/quote \
  -H "Content-Type: application/json" \
  -d '{
  "amount_usd": "50.00"
}'
```

### `POST /pay`

```bash
curl -X POST http://localhost:5000/pay \
  -H "Content-Type: application/json" \
  -d '{
  "quote_id": "abc-123",
  "payment_signature": "value"
}'
```

### `GET /balance`

```bash
curl http://localhost:5000/balance
```

### `GET /info`

```bash
curl http://localhost:5000/info
```

### `GET /quotes`

Returns all quotes.

```bash
curl http://localhost:5000/quotes
```

### `GET /payments`

Returns all payments.

```bash
curl http://localhost:5000/payments
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
