---
name: video-room-ai-meeting-moderator
title: "Video Room AI Meeting Moderator"
description: "Video Room AI Meeting Moderator — create video rooms with AI-powered agenda tracking and time management."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Video Room AI Meeting Moderator

Video Room AI Meeting Moderator — create video rooms with AI-powered agenda tracking and time management.

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
cd telnyx-code-examples/video-room-ai-meeting-moderator-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t video-room-ai-meeting-moderator .
docker run --env-file .env -p 5000:5000 video-room-ai-meeting-moderator
```

## API Reference

### `POST /rooms`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '{
  "agenda": "[]",
  "duration_minutes": 30,
  "name": "f\"meeting-{int(time.time(",
  "max_participants": 10,
  "id": "abc-123"
}'
```

**Response:**

```json
{
  "room_id": "...",
  "room": "..."
}
```

### `POST /rooms/<room_id>/start`

Handles `POST /rooms/<room_id>/start`.

**Request:**

```bash
curl -X POST http://localhost:5000/rooms/example-id/start
```

**Response:**

```json
{
  "status": "ok",
  "first_topic": "..."
}
```

### `GET /rooms/<room_id>/status`

Handles `GET /rooms/<room_id>/status`.

**Request:**

```bash
curl http://localhost:5000/rooms/example-id/status
```

**Response:**

```json
{
  "elapsed_minutes": "...",
  "remaining_minutes": "...",
  "current_topic": "...",
  "moderator_update": "...",
  "agenda": "..."
}
```

### `POST /rooms/<room_id>/next`

Handles `POST /rooms/<room_id>/next`.

**Request:**

```bash
curl -X POST http://localhost:5000/rooms/example-id/next
```

**Response:**

```json
{
  "next_topic": "...",
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
