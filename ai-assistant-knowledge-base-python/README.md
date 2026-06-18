---
name: ai-assistant-knowledge-base
title: "AI Assistant Knowledge Base"
description: "AI Assistant Knowledge Base — AI Assistant with document knowledge base for context-aware Q&A over uploaded documents."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Assistant Knowledge Base

AI Assistant Knowledge Base — AI Assistant with document knowledge base for context-aware Q&A over uploaded documents.

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
cd telnyx-code-examples/ai-assistant-knowledge-base-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-assistant-knowledge-base .
docker run --env-file .env -p 5000:5000 ai-assistant-knowledge-base
```

## API Reference

### `POST /documents`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/documents \
  -H "Content-Type: application/json" \
  -d '{
  "title": "f\"doc-{int(time.time(",
  "content": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok",
  "document": "..."
}
```

### `POST /ask`

Handles `POST /ask`.

**Request:**

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{
  "question": "example_value",
  "top_k": 3
}'
```

**Response:**

```json
{
  "answer": "...",
  "sources": "..."
}
```

### `GET /documents`

Returns all documents.

**Request:**

```bash
curl http://localhost:5000/documents
```

**Response:**

```json
{
  "documents": "...",
  "total_chunks": 3
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
