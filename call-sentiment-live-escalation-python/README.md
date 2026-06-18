---
name: call-sentiment-live-escalation
title: "Call Sentiment Live Escalation"
description: "Call Sentiment Live Escalation — monitor call transcripts in real-time. When negative sentiment or distress is detected, auto-escalate to a supervisor."
language: python
framework: flask
telnyx_products: [SMS/MMS, AI Inference]
---

# Call Sentiment Live Escalation

Call Sentiment Live Escalation — monitor call transcripts in real-time. When negative sentiment or distress is detected, auto-escalate to a supervisor.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)
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
| `SUPERVISOR_NUMBER` | `string` | `+18005551234` | **yes** | supervisor number | — |
| `CONNECTION_ID` | `string` | `1234567890` | **yes** | Call Control connection ID | [→ link](https://portal.telnyx.com/call-control/applications) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/call-sentiment-live-escalation-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t call-sentiment-live-escalation .
docker run --env-file .env -p 5000:5000 call-sentiment-live-escalation
```

## API Reference

### `POST /monitor`

Handles `POST /monitor`.

**Request:**

```bash
curl -X POST http://localhost:5000/monitor \
  -H "Content-Type: application/json" \
  -d '{
  "call_id": "abc-123",
  "agent": "Sarah Chen",
  "customer": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok",
  "call_id": "..."
}
```

### `POST /transcript`

Handles `POST /transcript`.

**Request:**

```bash
curl -X POST http://localhost:5000/transcript \
  -H "Content-Type: application/json" \
  -d '{
  "call_id": "abc-123",
  "speaker": "customer"
}'
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /calls/<call_id>/sentiment`

Handles `GET /calls/<call_id>/sentiment`.

**Request:**

```bash
curl http://localhost:5000/calls/example-id/sentiment
```

**Response:**

```json
{
  "call_id": "...",
  "avg_sentiment": "...",
  "trend": "...",
  "escalated": "...",
  "chunks": "..."
}
```

### `GET /escalations`

Returns all escalations.

**Request:**

```bash
curl http://localhost:5000/escalations
```

**Response:**

```json
{
  "escalations": "..."
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

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
