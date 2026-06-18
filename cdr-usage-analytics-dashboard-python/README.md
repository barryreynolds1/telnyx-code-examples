---
name: cdr-usage-analytics-dashboard
title: "CDR Usage Analytics Dashboard"
description: "Pull Call Detail Records, build usage analytics with cost breakdowns, peak-hour analysis, and AI-powered insights."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# CDR Usage Analytics Dashboard

Pull Call Detail Records, build usage analytics with cost breakdowns, peak-hour analysis, and AI-powered insights.

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
cd telnyx-code-examples/cdr-usage-analytics-dashboard-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t cdr-usage-analytics-dashboard .
docker run --env-file .env -p 5000:5000 cdr-usage-analytics-dashboard
```

## API Reference

### `GET /cdrs`

Returns cdrs details.

**Request:**

```bash
curl http://localhost:5000/cdrs
```

**Response:**

```json
{
  "cdrs": [
    "..."
  ]
}
```

### `GET /analytics/summary`

Handles `GET /analytics/summary`.

**Request:**

```bash
curl http://localhost:5000/analytics/summary
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /analytics/peak-hours`

Handles `GET /analytics/peak-hours`.

**Request:**

```bash
curl http://localhost:5000/analytics/peak-hours
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /analytics/top-routes`

Handles `GET /analytics/top-routes`.

**Request:**

```bash
curl http://localhost:5000/analytics/top-routes
```

**Response:**

```json
{
  "status": "ok"
}
```

### `GET /analytics/ai-insights`

Handles `GET /analytics/ai-insights`.

**Request:**

```bash
curl http://localhost:5000/analytics/ai-insights
```

**Response:**

```json
{
  "insights": "...",
  "summary": "..."
}
```

### `GET /analytics/daily`

Handles `GET /analytics/daily`.

**Request:**

```bash
curl http://localhost:5000/analytics/daily
```

**Response:**

```json
{
  "daily": "..."
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
