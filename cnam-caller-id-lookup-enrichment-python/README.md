---
name: cnam-caller-id-lookup-enrichment
title: "CNAM Caller ID Lookup Enrichment"
description: "CNAM Caller ID Lookup Enrichment — look up CNAM for inbound callers, enrich CRM records with caller identity."
language: python
framework: flask
telnyx_products: [Number Lookup]
channel: [voice]
---

# CNAM Caller ID Lookup Enrichment

CNAM Caller ID Lookup Enrichment — look up CNAM for inbound callers, enrich CRM records with caller identity.

## Telnyx API Endpoints Used

- **Number Lookup**: `GET /v2/number_lookup/{phone_number}` — [API reference](https://developers.telnyx.com/api/number-lookup/lookup)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.initiated` — incoming call detected, app answers

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│  Phone Call  │────►│   Telnyx   │────►│  POST /webhooks/voice│
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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/cnam-caller-id-lookup-enrichment-python
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

   - **Call Control Application** → Webhook URL → `https://<id>.ngrok.io/webhooks/voice`

### Docker

```bash
docker build -t cnam-caller-id-lookup-enrichment .
docker run --env-file .env -p 5000:5000 cnam-caller-id-lookup-enrichment
```

## API Reference

### `GET /lookup/<number>`

Handles `GET /lookup/<number>`.

**Request:**

```bash
curl http://localhost:5000/lookup/example-id
```

**Response:**

```json
{
  "result": "...",
  "source": "..."
}
```

### `POST /lookup/batch`

Handles `POST /lookup/batch`.

**Request:**

```bash
curl -X POST http://localhost:5000/lookup/batch \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "[]"
}'
```

**Response:**

```json
{
  "results": "...",
  "total": 3
}
```

### `GET /enrichments`

Returns all enrichments.

**Request:**

```bash
curl http://localhost:5000/enrichments
```

**Response:**

```json
{
  "enrichments": "..."
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

### `POST /webhooks/voice`

Receives [Telnyx Call Control](https://developers.telnyx.com/docs/voice/call-control) webhook events.

**Events handled:** `call.initiated`

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:uMi2qMWHT-mLFGkEm4t9tA",
    "connection_id": "1494404757140276705",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876",
    "call_leg_id": "428c31b6-7af4-4bcb-b7f5-5013ef9657c1",
    "client_state": null,
    "state": "ringing"
  },
  "meta": {
    "attempt": 1,
    "delivered_to": "https://your-server.example.com/webhooks/voice"
  }
}
```

## Resources

- [Number Lookup — API Reference](https://developers.telnyx.com/api/number-lookup/lookup)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
