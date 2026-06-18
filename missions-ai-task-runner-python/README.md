---
name: missions-ai-task-runner
title: "Missions AI Task Runner"
description: "Missions AI Task Runner — AI-driven task execution within the Telnyx Missions framework. AI decides next steps based on task results."
language: python
framework: flask
telnyx_products: [AI Inference, Number Lookup]
---

# Missions AI Task Runner

Missions AI Task Runner — AI-driven task execution within the Telnyx Missions framework. AI decides next steps based on task results.

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
cd telnyx-code-examples/missions-ai-task-runner-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t missions-ai-task-runner .
docker run --env-file .env -p 5000:5000 missions-ai-task-runner
```

## API Reference

### `POST /run`

Executes the batch workflow.

**Request:**

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
  "objective": "example_value",
  "context": "Customer reported issue with service",
  "max_steps": 5
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /runs`

Returns all runs.

**Request:**

```bash
curl http://localhost:5000/runs
```

**Response:**

```json
{
  "runs": "..."
}
```

### `GET /actions`

Returns all actions.

**Request:**

```bash
curl http://localhost:5000/actions
```

**Response:**

```json
{
  "actions": "..."
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
