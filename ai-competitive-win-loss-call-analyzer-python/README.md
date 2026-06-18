---
name: ai-competitive-win-loss-call-analyzer
title: "AI Competitive Win/Loss Call Analyzer"
description: "AI Competitive Win/Loss Call Analyzer — analyze recorded sales calls for competitive intelligence."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Competitive Win/Loss Call Analyzer

AI Competitive Win/Loss Call Analyzer — analyze recorded sales calls for competitive intelligence.

## Telnyx API Endpoints Used

- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

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
| `STORAGE_BUCKET` | `string` | `...` | **yes** | storage bucket | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-competitive-win-loss-call-analyzer-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-competitive-win-loss-call-analyzer .
docker run --env-file .env -p 5000:5000 ai-competitive-win-loss-call-analyzer
```

## API Reference

### `POST /analyze`

Handles `POST /analyze`.

**Request:**

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "example_value",
  "outcome": "unknown"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /insights`

Returns insights details.

**Request:**

```bash
curl http://localhost:5000/insights
```

**Response:**

```json
{
  "total_calls": 3,
  "insights": "..."
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
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
