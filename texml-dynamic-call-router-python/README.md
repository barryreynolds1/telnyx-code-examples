---
name: texml-dynamic-call-router
title: "TeXML Dynamic Call Router"
description: "TeXML Dynamic Call Router — time-of-day and caller-based routing with TeXML responses."
language: python
framework: flask
---

# TeXML Dynamic Call Router

TeXML Dynamic Call Router — time-of-day and caller-based routing with TeXML responses.

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
| `BUSINESS_HOURS_NUMBER` | `string` | `+18005551234` | **yes** | business hours number | — |
| `AFTER_HOURS_NUMBER` | `string` | `+18005551234` | **yes** | after hours number | — |
| `VOICEMAIL_URL` | `string` | `https://...` | no | voicemail url | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/texml-dynamic-call-router-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t texml-dynamic-call-router .
docker run --env-file .env -p 5000:5000 texml-dynamic-call-router
```

## API Reference

### `POST /texml/route`

Handles `POST /texml/route`.

**Request:**

```bash
curl -X POST http://localhost:5000/texml/route
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /texml/recording`

Handles `POST /texml/recording`.

**Request:**

```bash
curl -X POST http://localhost:5000/texml/recording
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /vip`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/vip \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe"
}'
```

**Response:**

```json
{
  "status": "ok",
  "phone": "..."
}
```

### `GET /calls`

Returns all calls.

**Request:**

```bash
curl http://localhost:5000/calls
```

**Response:**

```json
{
  "calls": "..."
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

- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
