# CDR Usage Analytics Dashboard

Pull Call Detail Records, build usage analytics with cost breakdowns, peak-hour analysis, and AI-powered insights.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t cdr-usage-analytics-dashboard .
docker run --env-file .env -p 5000:5000 cdr-usage-analytics-dashboard
```

## API Reference

### `GET /cdrs`

```bash
curl http://localhost:5000/cdrs
```

### `GET /analytics/summary`

```bash
curl http://localhost:5000/analytics/summary
```

### `GET /analytics/peak-hours`

```bash
curl http://localhost:5000/analytics/peak-hours
```

### `GET /analytics/top-routes`

```bash
curl http://localhost:5000/analytics/top-routes
```

### `GET /analytics/ai-insights`

```bash
curl http://localhost:5000/analytics/ai-insights
```

### `GET /analytics/daily`

```bash
curl http://localhost:5000/analytics/daily
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
