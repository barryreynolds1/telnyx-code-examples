# AI Competitive Win/Loss Call Analyzer — analyze recorded sales calls for competitive intelligence.

AI Competitive Win/Loss Call Analyzer — analyze recorded sales calls for competitive intelligence.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |
| Cloud Storage API | `S3-compatible` | [docs](https://developers.telnyx.com/docs/storage) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `STORAGE_BUCKET` | string | `-` | **yes** | storage bucket |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-competitive-win-loss-call-analyzer .
docker run --env-file .env -p 5000:5000 ai-competitive-win-loss-call-analyzer
```

## API Reference

### `POST /analyze`

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "value",
  "outcome": "unknown"
}'
```

### `GET /insights`

```bash
curl http://localhost:5000/insights
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
- [Cloud Storage API](https://developers.telnyx.com/docs/storage)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
