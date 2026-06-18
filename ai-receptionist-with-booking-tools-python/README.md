---
name: ai-receptionist-with-booking-tools
title: "AI Receptionist with Booking Tools"
description: "AI Receptionist with Booking Tools — AI Assistant with tool_use for real calendar booking actions."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Receptionist with Booking Tools

AI Receptionist with Booking Tools — AI Assistant with tool_use for real calendar booking actions.

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
| `ASSISTANT_ID` | `string` | `...` | **yes** | assistant id | — |
| `AI_MODEL` | `string` | `moonshotai/Kimi-K2.6` | no | Inference model identifier | [→ link](https://developers.telnyx.com/docs/inference/models) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-receptionist-with-booking-tools-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-receptionist-with-booking-tools .
docker run --env-file .env -p 5000:5000 ai-receptionist-with-booking-tools
```

## API Reference

### `POST /chat`

Handles `POST /chat`.

**Request:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
  "messages": "[]"
}'
```

**Response:**

```json
{
  "response": "...",
  "bookings": "..."
}
```

### `GET /bookings`

Returns all bookings.

**Request:**

```bash
curl http://localhost:5000/bookings
```

**Response:**

```json
{
  "bookings": "..."
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
