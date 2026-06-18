---
name: migrate-from-twilio
title: "Migrate from Twilio"
description: "Migrate from Twilio — complete Twilio-to-Telnyx migration tool: numbers, messaging profiles, voice apps, and webhook configs."
language: python
framework: flask
channel: [sms]
---

# Migrate from Twilio

Migrate from Twilio — complete Twilio-to-Telnyx migration tool: numbers, messaging profiles, voice apps, and webhook configs.

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│   SMS/MMS   │────►│   Telnyx   │────►│  POST /webhooks/sms  │
└─────────────┘     │   Cloud    │     └──────────┬───────────┘
                    └────────────┘                │
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
| `TWILIO_ACCOUNT_SID` | `string` | `...` | **yes** | twilio account sid | — |
| `TWILIO_AUTH_TOKEN` | `string` | `...` | **yes** | twilio auth token | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/migrate-from-twilio-python
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
docker build -t migrate-from-twilio .
docker run --env-file .env -p 5000:5000 migrate-from-twilio
```

## API Reference

### `GET /audit/twilio`

Handles `GET /audit/twilio`.

**Request:**

```bash
curl http://localhost:5000/audit/twilio
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /migrate/messaging-profile`

Handles `POST /migrate/messaging-profile`.

**Request:**

```bash
curl -X POST http://localhost:5000/migrate/messaging-profile \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Migrated from Twilio",
  "webhook_url": "https://pay.example.com/inv-123"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /migrate/numbers`

Handles `POST /migrate/numbers`.

**Request:**

```bash
curl -X POST http://localhost:5000/migrate/numbers \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "[]",
  "authorized_person": "example_value"
}'
```

**Response:**

```json
{
  "results": "..."
}
```

### `GET /migrate/code-changes`

Handles `GET /migrate/code-changes`.

**Request:**

```bash
curl http://localhost:5000/migrate/code-changes
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /migration-log`

Returns log details.

**Request:**

```bash
curl http://localhost:5000/migration-log
```

**Response:**

```json
{
  "log": "..."
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

### `POST /migrate/webhook-map`

Receives external webhook events.

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
