---
name: video-webinar-recording-manager
title: "Video Webinar Recording Manager"
description: "Video Webinar Recording Manager — manage video room webinars with automatic recording, transcription, and clip extraction."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Video Webinar Recording Manager

Video Webinar Recording Manager — manage video room webinars with automatic recording, transcription, and clip extraction.

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
cd telnyx-code-examples/video-webinar-recording-manager-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t video-webinar-recording-manager .
docker run --env-file .env -p 5000:5000 video-webinar-recording-manager
```

## API Reference

### `POST /webinars`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/webinars \
  -H "Content-Type: application/json" \
  -d '{
  "title": "example_value",
  "max_participants": 100,
  "host": "example_value",
  "scheduled": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /webinars/<room_id>/recordings`

Returns recordings details.

**Request:**

```bash
curl http://localhost:5000/webinars/example-id/recordings
```

**Response:**

```json
{
  "recordings": [
    "..."
  ]
}
```

### `POST /recordings/<recording_id>/transcribe`

Handles `POST /recordings/<recording_id>/transcribe`.

**Request:**

```bash
curl -X POST http://localhost:5000/recordings/example-id/transcribe \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /webinars`

Returns all webinars.

**Request:**

```bash
curl http://localhost:5000/webinars
```

**Response:**

```json
{
  "webinars": "..."
}
```

### `GET /recordings`

Returns all processed.

**Request:**

```bash
curl http://localhost:5000/recordings
```

**Response:**

```json
{
  "recordings": "..."
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
