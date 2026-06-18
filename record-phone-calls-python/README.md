---
name: record-phone-calls
title: "Production-ready Flask application for call recording via Telnyx Voice API."
description: "Production-ready Flask application for call recording via Telnyx Voice API."
language: python
framework: flask
---

# Production-ready Flask application for call recording via Telnyx Voice API.

Production-ready Flask application for call recording via Telnyx Voice API.

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `call.answered` — call connected, app speaks greeting
- `call.hangup` — call ended, app cleans up session

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
| `TELNYX_CONNECTION_ID` | `string` | `...` | **yes** | telnyx connection id | — |
| `FLASK_DEBUG` | `string` | `false` | no | flask debug | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/record-phone-calls-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t record-phone-calls .
docker run --env-file .env -p 5000:5000 record-phone-calls
```

## API Reference

### `POST /calls/initiate`

Handles `POST /calls/initiate`.

**Request:**

```bash
curl -X POST http://localhost:5000/calls/initiate
```

**Response:**

```json
{
  "status_code": "..."
}
```

### `POST /calls/<call_control_id>/recording/start`

Handles `POST /calls/<call_control_id>/recording/start`.

**Request:**

```bash
curl -X POST http://localhost:5000/calls/example-id/recording/start
```

**Response:**

```json
{
  "status_code": "..."
}
```

### `POST /calls/<call_control_id>/recording/stop`

Handles `POST /calls/<call_control_id>/recording/stop`.

**Request:**

```bash
curl -X POST http://localhost:5000/calls/example-id/recording/stop
```

**Response:**

```json
{
  "status_code": "..."
}
```

### `POST /calls/<call_control_id>/hangup`

Handles `POST /calls/<call_control_id>/hangup`.

**Request:**

```bash
curl -X POST http://localhost:5000/calls/example-id/hangup
```

**Response:**

```json
{
  "status_code": "..."
}
```

### `GET /calls/<call_control_id>/status`

Returns call status details.

**Request:**

```bash
curl http://localhost:5000/calls/example-id/status
```

**Response:**

```json
{
  "call_status": [
    "..."
  ]
}
```

## Webhook Endpoints

### `POST /webhooks/call-events`

Receives external webhook events.

## Resources

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
