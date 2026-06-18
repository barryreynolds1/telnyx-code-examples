# AI Call Center Quality Scorer — automatically score agent performance from call recordings on compliance, empathy, resolution, and talk-to-listen ratio.

AI Call Center Quality Scorer — automatically score agent performance from call recordings on compliance, empathy, resolution, and talk-to-listen ratio.

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
docker build -t ai-call-center-quality-scorer .
docker run --env-file .env -p 5000:5000 ai-call-center-quality-scorer
```

## API Reference

### `POST /score`

```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "value",
  "call_id": "f\"CALL-{int(time.time("
}'
```

### `POST /score/batch`

```bash
curl -X POST http://localhost:5000/score/batch \
  -H "Content-Type: application/json" \
  -d '{
  "transcripts": "value"
}'
```

### `GET /scorecards`

Returns all scorecards.

```bash
curl http://localhost:5000/scorecards
```

### `GET /scorecards/summary`

```bash
curl http://localhost:5000/scorecards/summary
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
