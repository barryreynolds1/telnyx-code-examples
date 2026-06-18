---
name: sms-trivia-game-tournament
title: "SMS Trivia Game Tournament"
description: "SMS Trivia Game Tournament — multi-player trivia via SMS. Players join, answer timed questions, scores tracked on a live leaderboard."
language: python
framework: flask
telnyx_products: [SMS/MMS, AI Inference]
channel: [sms]
---

# SMS Trivia Game Tournament

SMS Trivia Game Tournament — multi-player trivia via SMS. Players join, answer timed questions, scores tracked on a live leaderboard.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)
- **AI Inference (Chat Completions)**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Telnyx Webhook Events

This app handles these [Call Control](https://developers.telnyx.com/docs/api/v2/call-control) and [Messaging](https://developers.telnyx.com/docs/api/v2/messaging) webhook events:

- `message.received` — inbound SMS/MMS received

## Architecture

```text
┌─────────────┐     ┌────────────┐     ┌──────────────────────┐
│   SMS/MMS   │────►│   Telnyx   │────►│  POST /webhooks/sms  │
└─────────────┘     │   Cloud    │     └──────────┬───────────┘
                    └────────────┘                │
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
| `TRIVIA_NUMBER` | `string` | `+18005551234` | **yes** | trivia number | — |
| `MESSAGING_PROFILE_ID` | `string` | `4001...` | no | Telnyx messaging profile ID | [→ link](https://portal.telnyx.com/messaging/profiles) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sms-trivia-game-tournament-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Webhook Configuration

1. Expose your local server:

   ```bash
   ngrok http 5000
   ```

2. Copy the HTTPS URL and configure in [Telnyx Portal](https://portal.telnyx.com):

   - **Messaging Profile** → Inbound Webhook URL → `https://<id>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t sms-trivia-game-tournament .
docker run --env-file .env -p 5000:5000 sms-trivia-game-tournament
```

## API Reference

### `POST /tournament/create`

Creates a new record.

**Request:**

```bash
curl -X POST http://localhost:5000/tournament/create \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Trivia Night",
  "category": "general",
  "rounds": 5
}'
```

**Response:**

```json
{
  "tournament_id": "...",
  "join_code": "..."
}
```

### `POST /tournament/<tid>/next`

Handles `POST /tournament/<tid>/next`.

**Request:**

```bash
curl -X POST http://localhost:5000/tournament/example-id/next
```

**Response:**

```json
{
  "status": "ok",
  "round": "...",
  "question": "..."
}
```

### `GET /tournament/<tid>/leaderboard`

Handles `GET /tournament/<tid>/leaderboard`.

**Request:**

```bash
curl http://localhost:5000/tournament/example-id/leaderboard
```

**Response:**

```json
{
  "leaderboard": "..."
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

## Webhook Endpoints

### `POST /webhooks/messaging`

Receives [Telnyx Messaging](https://developers.telnyx.com/docs/messaging) webhook events.

**Example inbound payload:**

```json
{
  "data": {
    "event_type": "message.received",
    "direction": "inbound",
    "payload": {
      "id": "f5d7a7e0-1234-5678-9abc-def012345678",
      "from": {
        "phone_number": "+12125551234",
        "carrier": "Verizon",
        "line_type": "Wireless"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "HELP",
      "type": "SMS",
      "media": [],
      "received_at": "2026-07-15T14:30:00Z"
    }
  }
}
```

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
