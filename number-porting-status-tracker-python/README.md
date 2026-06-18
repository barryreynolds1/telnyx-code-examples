---
name: number-porting-status-tracker
title: "Number Porting Status Tracker"
description: "Number Porting Status Tracker — track porting orders with status webhooks and SMS alerts."
language: python
framework: flask
telnyx_products: [SMS/MMS]
---

# Number Porting Status Tracker

Number Porting Status Tracker — track porting orders with status webhooks and SMS alerts.

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
| `ALERT_NUMBER` | `string` | `+18005551234` | **yes** | alert number | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/number-porting-status-tracker-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t number-porting-status-tracker .
docker run --env-file .env -p 5000:5000 number-porting-status-tracker
```

## API Reference

### `GET /ports/list`

Returns all ports.

**Request:**

```bash
curl http://localhost:5000/ports/list
```

**Response:**

```json
{
  "ports": [
    "..."
  ]
}
```

### `POST /ports/create`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/ports/create \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "[]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /ports/<order_id>`

Returns port details.

**Request:**

```bash
curl http://localhost:5000/ports/example-id
```

**Response:**

```json
{
  "port": [
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

### `POST /webhooks/porting`

Receives external webhook events.

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
