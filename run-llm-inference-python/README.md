# Run LLM inference on Telnyx — OpenAI-compatible chat completions API.

Run LLM inference on Telnyx — OpenAI-compatible chat completions API.

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
| `FLASK_DEBUG` | string | `-` | no | flask debug |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t run-llm-inference .
docker run --env-file .env -p 5000:5000 run-llm-inference
```

## API Reference

### `POST /inference/chat`

```bash
curl -X POST http://localhost:5000/inference/chat \
  -H "Content-Type: application/json" \
  -d '{
  "model": "value",
  "max_tokens": "500",
  "temperature": "0.7"
}'
```

### `POST /inference/ask`

```bash
curl -X POST http://localhost:5000/inference/ask \
  -H "Content-Type: application/json" \
  -d '{
  "system_prompt": "value"
}'
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
