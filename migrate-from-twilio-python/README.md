# Migrate from Twilio — complete Twilio-to-Telnyx migration tool: numbers, messaging profiles, voice apps, and webhook configs.

Migrate from Twilio — complete Twilio-to-Telnyx migration tool: numbers, messaging profiles, voice apps, and webhook configs.

## How It Works

```
Inbound SMS ──► Telnyx ──► POST /webhooks/sms
                                   │
                                   ├── Takes action
                                   └── Sends reply SMS
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `TWILIO_ACCOUNT_SID` | string | `-` | **yes** | twilio account sid |
| `TWILIO_AUTH_TOKEN` | string | `token` | **yes** | twilio auth token |

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
docker build -t migrate-from-twilio .
docker run --env-file .env -p 5000:5000 migrate-from-twilio
```

## API Reference

### `GET /audit/twilio`

```bash
curl http://localhost:5000/audit/twilio
```

### `POST /migrate/messaging-profile`

```bash
curl -X POST http://localhost:5000/migrate/messaging-profile \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Migrated from Twilio",
  "webhook_url": "value"
}'
```

### `POST /migrate/numbers`

```bash
curl -X POST http://localhost:5000/migrate/numbers \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "+12125551234",
  "authorized_person": "value"
}'
```

### `GET /migrate/code-changes`

```bash
curl http://localhost:5000/migrate/code-changes
```

### `GET /migration-log`

```bash
curl http://localhost:5000/migration-log
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

### `POST /migrate/webhook-map`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
