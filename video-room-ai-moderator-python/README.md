---
name: video-room-ai-moderator
title: "Video Room AI Moderator"
description: "Video Room AI Moderator — create video rooms with AI-powered content moderation on chat and participant management."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Video Room AI Moderator

Video Room AI Moderator — create video rooms with AI-powered content moderation on chat and participant management.

## Telnyx API Endpoints Used

- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
                                                   │
                                          ┌────────┴────────┐
                                          │ Telnyx Inference │
                                          │ (AI processing) │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Response (SMS/  │
                                          │ Voice/Webhook)  │
                                          └─────────────────┘
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Type | Example | Required | Description | Where to get it |
|----------|------|---------|----------|-------------|-----------------|
| `TELNYX_API_KEY` | `string` | `KEY...` | **yes** | Telnyx API v2 key | [→ link](https://portal.telnyx.com/api-keys) |
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/video-room-ai-moderator-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t video-room-ai-moderator .
docker run --env-file .env -p 5000:5000 video-room-ai-moderator
```

## API Reference

### `POST /rooms`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "max_participants": 10,
  "record": "False",
  "rules": "[\"no_profanity\", \"no_harassment\", \"no_spam\"]"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /rooms`

Returns all rooms.

**Request:**

```bash
curl http://localhost:5000/rooms
```

**Response:**

```json
{
  "rooms": [
    "..."
  ]
}
```

### `POST /rooms/<room_id>/tokens`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/rooms/example-id/tokens
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /moderate`

Handles `POST /moderate`.

**Request:**

```bash
curl -X POST http://localhost:5000/moderate \
  -H "Content-Type: application/json" \
  -d '{
  "room_id": "abc-123",
  "message": "Customer reported issue with service",
  "sender": "unknown"
}'
```

**Response:**

```json
{
  "moderation": "..."
}
```

### `GET /moderation-log`

Returns log details.

**Request:**

```bash
curl http://localhost:5000/moderation-log
```

**Response:**

```json
{
  "log": "..."
}
```

### `DELETE /rooms/<room_id>`

Handles `DELETE /rooms/<room_id>`.

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /health`

Returns service health and operational metrics.

**Request:**

```bash
curl http://localhost:5000/health
```

**Response:**

```json
{
  "status": "ok"
}
```

## Resources

- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
