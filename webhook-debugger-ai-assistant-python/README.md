# Webhook Debugger AI Assistant — catch, inspect, and debug Telnyx webhooks with AI explanations.

Webhook Debugger AI Assistant — catch, inspect, and debug Telnyx webhooks with AI explanations.

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
docker build -t webhook-debugger-ai-assistant .
docker run --env-file .env -p 5000:5000 webhook-debugger-ai-assistant
```

## API Reference

### `GET /catch/<path:subpath>`

```bash
curl http://localhost:5000/catch/<path:subpath>
```

### `POST /catch/<path:subpath>`

```bash
curl -X POST http://localhost:5000/catch/<path:subpath> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `PUT /catch/<path:subpath>`

```bash
curl -X PUT http://localhost:5000/catch/<path:subpath> \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `DELETE /catch/<path:subpath>`

### `GET /analyze/<int:index>`

```bash
curl http://localhost:5000/analyze/<int:index>
```

### `GET /analyze/recent`

```bash
curl http://localhost:5000/analyze/recent
```

### `GET /log`

```bash
curl http://localhost:5000/log
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
