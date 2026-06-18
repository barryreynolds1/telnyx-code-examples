---
name: send-mms-picture-message
title: "Production-ready Flask endpoint for sending MMS via Telnyx."
description: "Production-ready Flask endpoint for sending MMS via Telnyx."
language: python
framework: flask
---

# Production-ready Flask endpoint for sending MMS via Telnyx.

Production-ready Flask endpoint for sending MMS via Telnyx.

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
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
| `FLASK_DEBUG` | `string` | `false` | no | flask debug | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-mms-picture-message-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t send-mms-picture-message .
docker run --env-file .env -p 5000:5000 send-mms-picture-message
```

## API Reference

### `POST /mms/send`

Sends notifications to applicable recipients.

**Request:**

```bash
curl -X POST http://localhost:5000/mms/send \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Customer reported issue with service",
  "media_urls": "[]"
}'
```

**Response:**

```json
{
  "status_code": "..."
}
```

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
