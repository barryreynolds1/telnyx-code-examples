# AI Assistant Phone Setup — create and configure a managed Telnyx AI Assistant and wire it to a phone number.

AI Assistant Phone Setup — create and configure a managed Telnyx AI Assistant and wire it to a phone number.

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

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-assistant-phone-setup .
docker run --env-file .env -p 5000:5000 ai-assistant-phone-setup
```

## API Reference

### `POST /assistants`

Create a new record.

```bash
curl -X POST http://localhost:5000/assistants \
  -H "Content-Type: application/json" \
  -d '{
  "name": "My Assistant",
  "instructions": "You are a helpful assistant. Be friendly and concise.",
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "voice_provider": "telnyx",
  "voice_id": "en-US-Neural2-F",
  "speed": "1.0",
  "greeting": "Hello! How can I help you today?",
  "hold_music_url": "value"
}'
```

### `GET /assistants`

Returns all assistants.

```bash
curl http://localhost:5000/assistants
```

### `GET /assistants/<assistant_id>`

```bash
curl http://localhost:5000/assistants/<assistant_id>
```

### `PATCH /assistants/<assistant_id>`

Update record status.

### `POST /assistants/<assistant_id>/wire`

```bash
curl -X POST http://localhost:5000/assistants/<assistant_id>/wire \
  -H "Content-Type: application/json" \
  -d '{
  "phone_number": "+12125551234"
}'
```

### `POST /assistants/<assistant_id>/test`

```bash
curl -X POST http://localhost:5000/assistants/<assistant_id>/test \
  -H "Content-Type: application/json" \
  -d '{
  "message": "Hello"
}'
```

### `GET /models`

Returns all models.

```bash
curl http://localhost:5000/models
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
