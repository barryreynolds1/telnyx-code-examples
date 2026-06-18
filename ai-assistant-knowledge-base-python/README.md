# AI Assistant Knowledge Base — AI Assistant with document knowledge base for context-aware Q&A over uploaded documents.

AI Assistant Knowledge Base — AI Assistant with document knowledge base for context-aware Q&A over uploaded documents.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

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
docker build -t ai-assistant-knowledge-base .
docker run --env-file .env -p 5000:5000 ai-assistant-knowledge-base
```

## API Reference

### `POST /documents`

Create a new record.

```bash
curl -X POST http://localhost:5000/documents \
  -H "Content-Type: application/json" \
  -d '{
  "title": "f\"doc-{int(time.time(",
  "content": "value"
}'
```

### `POST /ask`

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{
  "question": "value",
  "top_k": "3"
}'
```

### `GET /documents`

Returns all documents.

```bash
curl http://localhost:5000/documents
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
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
