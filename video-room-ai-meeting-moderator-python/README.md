# Video Room AI Meeting Moderator — create video rooms with AI-powered agenda tracking and time management.

Video Room AI Meeting Moderator — create video rooms with AI-powered agenda tracking and time management.

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
docker build -t video-room-ai-meeting-moderator .
docker run --env-file .env -p 5000:5000 video-room-ai-meeting-moderator
```

## API Reference

### `POST /rooms`

Create a new record.

```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{
  "agenda": "value",
  "duration_minutes": "30",
  "name": "f\"meeting-{int(time.time(",
  "max_participants": "10",
  "id": "abc-123"
}'
```

### `POST /rooms/<room_id>/start`

```bash
curl -X POST http://localhost:5000/rooms/<room_id>/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /rooms/<room_id>/status`

Update record status.

```bash
curl http://localhost:5000/rooms/<room_id>/status
```

### `POST /rooms/<room_id>/next`

```bash
curl -X POST http://localhost:5000/rooms/<room_id>/next \
  -H "Content-Type: application/json" \
  -d '{}'
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
