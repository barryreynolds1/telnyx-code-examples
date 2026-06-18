---
name: number-warmup-reputation-builder
title: "Number Warmup & Reputation Builder"
description: "Number Warmup & Reputation Builder — gradually ramp SMS volume on new numbers to build carrier reputation and avoid spam flags."
language: python
framework: flask
telnyx_products: [SMS/MMS]
---

# Number Warmup & Reputation Builder

Number Warmup & Reputation Builder — gradually ramp SMS volume on new numbers to build carrier reputation and avoid spam flags.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)

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
| `MESSAGING_PROFILE_ID` | `string` | `4001...` | no | Telnyx messaging profile ID | [→ link](https://portal.telnyx.com/messaging/profiles) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/number-warmup-reputation-builder-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t number-warmup-reputation-builder .
docker run --env-file .env -p 5000:5000 number-warmup-reputation-builder
```

## API Reference

### `POST /warmup/start`

Handles `POST /warmup/start`.

**Request:**

```bash
curl -X POST http://localhost:5000/warmup/start \
  -H "Content-Type: application/json" \
  -d '{
  "number": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok",
  "number": "...",
  "schedule": "..."
}
```

### `POST /warmup/send`

Sends notifications to applicable recipients.

**Request:**

```bash
curl -X POST http://localhost:5000/warmup/send \
  -H "Content-Type: application/json" \
  -d '{
  "from_number": "example_value"
}'
```

**Response:**

```json
{
  "limit": "...",
  "sent": "...",
  "wait_seconds": "...",
  "status": "ok",
  "day": "...",
  "today_count": 3
}
```

### `GET /warmup/status`

Handles `GET /warmup/status`.

**Request:**

```bash
curl http://localhost:5000/warmup/status
```

**Response:**

```json
{
  "numbers": "..."
}
```

### `POST /warmup/reset-daily`

Handles `POST /warmup/reset-daily`.

**Request:**

```bash
curl -X POST http://localhost:5000/warmup/reset-daily
```

**Response:**

```json
{
  "status": "ok",
  "numbers": "..."
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

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
