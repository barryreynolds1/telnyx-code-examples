# Video Room AI Moderator — create video rooms with AI-powered content moderation on chat and participant management.

Video Room AI Moderator — create video rooms with AI-powered content moderation on chat and participant management.

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
docker build -t video-room-ai-moderator .
docker run --env-file .env -p 5000:5000 video-room-ai-moderator
```

## API Reference

### `POST /rooms`

Create a new record.

```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "max_participants": "10",
  "record": "False",
  "rules": "[\"no_profanity\", \"no_harassment\", \"no_spam\"]"
}'
```

### `GET /rooms`

Returns all rooms.

```bash
curl http://localhost:5000/rooms
```

### `POST /rooms/<room_id>/tokens`

Create a new record.

```bash
curl -X POST http://localhost:5000/rooms/<room_id>/tokens \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /moderate`

```bash
curl -X POST http://localhost:5000/moderate \
  -H "Content-Type: application/json" \
  -d '{
  "room_id": "abc-123",
  "message": "Hello, this is a test",
  "sender": "unknown"
}'
```

### `GET /moderation-log`

```bash
curl http://localhost:5000/moderation-log
```

### `DELETE /rooms/<room_id>`

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
