---
name: missions-workflow-orchestrator
title: "Missions Workflow Orchestrator"
description: "Missions Workflow Orchestrator — create and manage multi-step mission workflows using the Telnyx Missions API."
language: python
framework: flask
---

# Missions Workflow Orchestrator

Missions Workflow Orchestrator — create and manage multi-step mission workflows using the Telnyx Missions API.

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
cd telnyx-code-examples/missions-workflow-orchestrator-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t missions-workflow-orchestrator .
docker run --env-file .env -p 5000:5000 missions-workflow-orchestrator
```

## API Reference

### `POST /missions`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/missions \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "description": "Customer reported issue with service",
  "tasks": "[]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /missions`

Returns all missions.

**Request:**

```bash
curl http://localhost:5000/missions
```

**Response:**

```json
{
  "local": "..."
}
```

### `GET /missions/<mission_id>`

Returns mission details.

**Request:**

```bash
curl http://localhost:5000/missions/example-id
```

**Response:**

```json
{
  "mission": [
    "..."
  ]
}
```

### `POST /missions/<mission_id>/tasks`

Adds a new entry.

**Request:**

```bash
curl -X POST http://localhost:5000/missions/example-id/tasks \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "type": "action",
  "config": "example_value",
  "depends_on": "[]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /missions/<mission_id>/run`

Executes the batch workflow.

**Request:**

```bash
curl -X POST http://localhost:5000/missions/example-id/run
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /missions/<mission_id>/runs`

Returns all runs.

**Request:**

```bash
curl http://localhost:5000/missions/example-id/runs
```

**Response:**

```json
{
  "runs": [
    "..."
  ]
}
```

### `GET /templates`

Handles `GET /templates`.

**Request:**

```bash
curl http://localhost:5000/templates
```

**Response:**

```json
{
  "status": "ok"
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
