# Missions Workflow Orchestrator — create and manage multi-step mission workflows using the Telnyx Missions API.

Missions Workflow Orchestrator — create and manage multi-step mission workflows using the Telnyx Missions API.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t missions-workflow-orchestrator .
docker run --env-file .env -p 5000:5000 missions-workflow-orchestrator
```

## API Reference

### `POST /missions`

Create a new record.

```bash
curl -X POST http://localhost:5000/missions \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "description": "value",
  "tasks": "value"
}'
```

### `GET /missions`

Returns all missions.

```bash
curl http://localhost:5000/missions
```

### `GET /missions/<mission_id>`

```bash
curl http://localhost:5000/missions/<mission_id>
```

### `POST /missions/<mission_id>/tasks`

Create a new record.

```bash
curl -X POST http://localhost:5000/missions/<mission_id>/tasks \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "type": "action",
  "config": "value",
  "depends_on": "value"
}'
```

### `POST /missions/<mission_id>/run`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/missions/<mission_id>/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /missions/<mission_id>/runs`

Returns all runs.

```bash
curl http://localhost:5000/missions/<mission_id>/runs
```

### `GET /templates`

```bash
curl http://localhost:5000/templates
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
