---
name: number-lookup-lead-enrichment
title: "Number Lookup Lead Enrichment"
description: "Number Lookup Lead Enrichment — CNAM and carrier lookup to qualify and enrich sales leads."
language: python
framework: flask
telnyx_products: [AI Inference, Number Lookup]
---

# Number Lookup Lead Enrichment

Number Lookup Lead Enrichment — CNAM and carrier lookup to qualify and enrich sales leads.

## Telnyx API Endpoints Used

- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)
- **Number Lookup**: `GET /v2/number_lookup/{phone_number}` — [API reference](https://developers.telnyx.com/api/number-lookup/lookup)

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
                                                   │
                                          ┌────────┴────────┐
                                          │ Telnyx Inference │
                                          │ (AI processing) │
                                          └────────┬────────┘
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
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/number-lookup-lead-enrichment-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t number-lookup-lead-enrichment .
docker run --env-file .env -p 5000:5000 number-lookup-lead-enrichment
```

## API Reference

### `POST /enrich`

Handles `POST /enrich`.

**Request:**

```bash
curl -X POST http://localhost:5000/enrich
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /enrich/bulk`

Handles `POST /enrich/bulk`.

**Request:**

```bash
curl -X POST http://localhost:5000/enrich/bulk \
  -H "Content-Type: application/json" \
  -d '{
  "phone_numbers": "[]"
}'
```

**Response:**

```json
{
  "results": "...",
  "total": 3
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

- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Number Lookup — API Reference](https://developers.telnyx.com/api/number-lookup/lookup)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
