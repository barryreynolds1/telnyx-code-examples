# Video Webinar Recording Manager — manage video room webinars with automatic recording, transcription, and clip extraction.

Video Webinar Recording Manager — manage video room webinars with automatic recording, transcription, and clip extraction.

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
docker build -t video-webinar-recording-manager .
docker run --env-file .env -p 5000:5000 video-webinar-recording-manager
```

## API Reference

### `POST /webinars`

Create a new record.

```bash
curl -X POST http://localhost:5000/webinars \
  -H "Content-Type: application/json" \
  -d '{
  "title": "value",
  "max_participants": "100",
  "host": "value",
  "scheduled": "value"
}'
```

### `GET /webinars/<room_id>/recordings`

```bash
curl http://localhost:5000/webinars/<room_id>/recordings
```

### `POST /recordings/<recording_id>/transcribe`

```bash
curl -X POST http://localhost:5000/recordings/<recording_id>/transcribe \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "value"
}'
```

### `GET /webinars`

Returns all webinars.

```bash
curl http://localhost:5000/webinars
```

### `GET /recordings`

Returns all processed.

```bash
curl http://localhost:5000/recordings
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
