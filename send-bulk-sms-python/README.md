---
name: send-bulk-sms
title: "Production-ready Flask application for sending bulk SMS via Telnyx."
description: "Production-ready Flask application for sending bulk SMS via Telnyx."
language: python
framework: flask
channel: [sms]
---

# Production-ready Flask application for sending bulk SMS via Telnyx.

Production-ready Flask application for sending bulk SMS via Telnyx.

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
| `TELNYX_PHONE_NUMBER` | `string` | `+18005551234` | **yes** | telnyx phone number | — |
| `BULK_SMS_RATE_LIMIT` | `string` | `10` | no | bulk sms rate limit | — |
| `BULK_SMS_DELAY` | `string` | `0.1` | no | bulk sms delay | — |
| `FLASK_DEBUG` | `string` | `false` | no | flask debug | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-bulk-sms-python
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
docker build -t send-bulk-sms .
docker run --env-file .env -p 5000:5000 send-bulk-sms
```

## API Reference

### `POST /sms/bulk/send`

Sends notifications to applicable recipients.

**Request:**

```bash
curl -X POST http://localhost:5000/sms/bulk/send \
  -H "Content-Type: application/json" \
  -d '{
  "recipients": "[]",
  "message": "Customer reported issue with service"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /sms/bulk/status`

Handles `GET /sms/bulk/status`.

**Request:**

```bash
curl http://localhost:5000/sms/bulk/status
```

**Response:**

```json
{
  "service": "...",
  "status": "ok",
  "rate_limit": "...",
  "delay_between_messages": "..."
}
```

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
