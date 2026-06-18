---
name: click-to-call-webrtc-with-ai-assist
title: "Click-to-Call WebRTC with AI Assist"
description: "Click-to-Call WebRTC with AI Assist — browser-based calling with real-time AI coaching sidebar."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# Click-to-Call WebRTC with AI Assist

Click-to-Call WebRTC with AI Assist — browser-based calling with real-time AI coaching sidebar.

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
| `WEBRTC_CREDENTIAL_ID` | `string` | `...` | **yes** | webrtc credential id | — |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/click-to-call-webrtc-with-ai-assist-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t click-to-call-webrtc-with-ai-assist .
docker run --env-file .env -p 5000:5000 click-to-call-webrtc-with-ai-assist
```

## API Reference

### `GET /`

Handles `GET /`.

**Request:**

```bash
curl http://localhost:5000/
```

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /webrtc/token`

Returns token details.

**Request:**

```bash
curl -X POST http://localhost:5000/webrtc/token
```

**Response:**

```json
{
  "token": [
    "..."
  ]
}
```

### `POST /coaching`

Returns coaching details.

**Request:**

```bash
curl -X POST http://localhost:5000/coaching \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "example_value"
}'
```

**Response:**

```json
{
  "coaching_tip": "..."
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
