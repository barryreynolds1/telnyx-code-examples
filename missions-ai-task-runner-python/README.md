# Missions AI Task Runner — AI-driven task execution within the Telnyx Missions framework. AI decides next steps based on task results.

Missions AI Task Runner — AI-driven task execution within the Telnyx Missions framework. AI decides next steps based on task results.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |
| Number Lookup API | `GET /v2/number_lookup/{number}` | [docs](https://developers.telnyx.com/docs/numbers) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t missions-ai-task-runner .
docker run --env-file .env -p 5000:5000 missions-ai-task-runner
```

## API Reference

### `POST /run`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
  "objective": "value",
  "context": "Hello, this is a test",
  "max_steps": "5"
}'
```

### `GET /runs`

Returns all runs.

```bash
curl http://localhost:5000/runs
```

### `GET /actions`

Returns all actions.

```bash
curl http://localhost:5000/actions
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

- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Number Lookup API](https://developers.telnyx.com/docs/numbers)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
