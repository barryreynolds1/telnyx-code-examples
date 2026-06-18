# AI Assistant Multi-Tool — AI Assistant with custom function-calling tools for CRM lookup, appointment booking, and order status.

AI Assistant Multi-Tool — AI Assistant with custom function-calling tools for CRM lookup, appointment booking, and order status.

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
docker build -t ai-assistant-multi-tool .
docker run --env-file .env -p 5000:5000 ai-assistant-multi-tool
```

## API Reference

### `POST /chat`

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
  "messages": "Hello, this is a test"
}'
```

### `GET /tools`

Returns all tools.

```bash
curl http://localhost:5000/tools
```

### `GET /tool-calls`

Returns all tool calls.

```bash
curl http://localhost:5000/tool-calls
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
