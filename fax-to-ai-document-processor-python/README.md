---
name: fax-to-ai-document-processor
title: "Fax to AI Document Processor"
description: "Fax to AI Document Processor — receive fax, AI extracts data, forwards structured summary."
language: python
framework: flask
telnyx_products: [SMS/MMS, AI Inference]
---

# Fax to AI Document Processor

Fax to AI Document Processor — receive fax, AI extracts data, forwards structured summary.

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
| `FAX_NUMBER` | `string` | `+18005551234` | **yes** | fax number | — |
| `FORWARD_EMAIL` | `string` | `...` | **yes** | forward email | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/fax-to-ai-document-processor-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t fax-to-ai-document-processor .
docker run --env-file .env -p 5000:5000 fax-to-ai-document-processor
```

## API Reference

### `GET /faxes`

Returns all faxes.

**Request:**

```bash
curl http://localhost:5000/faxes
```

**Response:**

```json
{
  "faxes": "..."
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

### `POST /webhooks/fax`

Receives external webhook events.

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [AI Inference (Chat Completions) — API Reference](https://developers.telnyx.com/api/inference/chat-completions)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
