---
name: ai-call-center-quality-scorer
title: "AI Call Center Quality Scorer"
description: "AI Call Center Quality Scorer — automatically score agent performance from call recordings on compliance, empathy, resolution, and talk-to-listen ratio."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Call Center Quality Scorer

AI Call Center Quality Scorer — automatically score agent performance from call recordings on compliance, empathy, resolution, and talk-to-listen ratio.

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

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-call-center-quality-scorer-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-call-center-quality-scorer .
docker run --env-file .env -p 5000:5000 ai-call-center-quality-scorer
```

## API Reference

### `POST /score`

Handles `POST /score`.

**Request:**

```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "example_value",
  "call_id": "f\"CALL-{int(time.time("
}'
```

**Response:**

```json
{
  "raw_analysis": "..."
}
```

### `POST /score/batch`

Handles `POST /score/batch`.

**Request:**

```bash
curl -X POST http://localhost:5000/score/batch \
  -H "Content-Type: application/json" \
  -d '{
  "transcripts": "[]"
}'
```

**Response:**

```json
{
  "results": "..."
}
```

### `GET /scorecards`

Returns all scorecards.

**Request:**

```bash
curl http://localhost:5000/scorecards
```

**Response:**

```json
{
  "scorecards": "..."
}
```

### `GET /scorecards/summary`

Handles `GET /scorecards/summary`.

**Request:**

```bash
curl http://localhost:5000/scorecards/summary
```

**Response:**

```json
{
  "message": "...",
  "count": 3,
  "avg_overall": "...",
  "avg_empathy": "...",
  "avg_compliance": "...",
  "avg_resolution": "..."
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
