---
name: sip-trunking-failover-monitor
title: "SIP Trunking Failover Monitor"
description: "SIP Trunking Failover Monitor — health-check SIP connections, auto-failover, SMS alerts."
language: python
framework: flask
telnyx_products: [SMS/MMS, AI Inference]
---

# SIP Trunking Failover Monitor

SIP Trunking Failover Monitor — health-check SIP connections, auto-failover, SMS alerts.

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
| `ALERT_NUMBER` | `string` | `+18005551234` | **yes** | alert number | — |
| `PRIMARY_SIP_CONNECTION_ID` | `string` | `...` | **yes** | primary sip connection id | — |
| `BACKUP_SIP_CONNECTION_ID` | `string` | `...` | **yes** | backup sip connection id | — |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sip-trunking-failover-monitor-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t sip-trunking-failover-monitor .
docker run --env-file .env -p 5000:5000 sip-trunking-failover-monitor
```

## API Reference

### `POST /check`

Returns service health and operational metrics.

**Request:**

```bash
curl -X POST http://localhost:5000/check
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /status`

Returns status details.

**Request:**

```bash
curl http://localhost:5000/status
```

**Response:**

```json
{
  "active_connection": 3,
  "primary_id": "...",
  "backup_id": "...",
  "recent_checks": "..."
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
