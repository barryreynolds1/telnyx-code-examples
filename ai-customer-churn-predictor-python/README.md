---
name: ai-customer-churn-predictor
title: "AI Customer Churn Predictor"
description: "AI Customer Churn Predictor — analyze call/message patterns via Telnyx APIs, AI predicts churn risk and suggests interventions."
language: python
framework: flask
telnyx_products: [AI Inference]
---

# AI Customer Churn Predictor

AI Customer Churn Predictor — analyze call/message patterns via Telnyx APIs, AI predicts churn risk and suggests interventions.

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
cd telnyx-code-examples/ai-customer-churn-predictor-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-customer-churn-predictor .
docker run --env-file .env -p 5000:5000 ai-customer-churn-predictor
```

## API Reference

### `POST /predict`

Handles `POST /predict`.

**Request:**

```bash
curl -X POST http://localhost:5000/predict
```

**Response:**

```json
{
  "raw": "..."
}
```

### `POST /predict/batch`

Handles `POST /predict/batch`.

**Request:**

```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
  "customers": "[]"
}'
```

**Response:**

```json
{
  "results": "...",
  "high_risk_count": 3
}
```

### `GET /predictions`

Returns all predictions.

**Request:**

```bash
curl http://localhost:5000/predictions
```

**Response:**

```json
{
  "predictions": "..."
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
