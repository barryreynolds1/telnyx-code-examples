---
name: bulk-number-validation-cleaner
title: "Bulk Number Validation & Cleaner"
description: "Bulk Number Validation & Cleaner — validate and clean phone number lists via Telnyx Number Lookup API."
language: python
framework: flask
telnyx_products: [Number Lookup]
---

# Bulk Number Validation & Cleaner

Bulk Number Validation & Cleaner — validate and clean phone number lists via Telnyx Number Lookup API.

## Telnyx API Endpoints Used

- **Number Lookup**: `GET /v2/number_lookup/{phone_number}` — [API reference](https://developers.telnyx.com/api/number-lookup/lookup)

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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/bulk-number-validation-cleaner-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t bulk-number-validation-cleaner .
docker run --env-file .env -p 5000:5000 bulk-number-validation-cleaner
```

## API Reference

### `POST /validate`

Handles `POST /validate`.

**Request:**

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "[]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /validate/single/<number>`

Handles `GET /validate/single/<number>`.

**Request:**

```bash
curl http://localhost:5000/validate/single/example-id
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /jobs`

Returns all jobs.

**Request:**

```bash
curl http://localhost:5000/jobs
```

**Response:**

```json
{
  "jobs": "..."
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

- [Number Lookup — API Reference](https://developers.telnyx.com/api/number-lookup/lookup)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
