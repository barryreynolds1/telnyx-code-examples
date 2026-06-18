# AI-Powered IVR Replacement — natural language routing with A/B testing and structured insights.

AI-Powered IVR Replacement — natural language routing with A/B testing and structured insights.

## Webhook Events Handled

```
call.initiated
```

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `ASSISTANT_ID` | string | `-` | **yes** | assistant id |
| `FLASK_DEBUG` | string | `-` | no | flask debug |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t ai-powered-ivr-replacement .
docker run --env-file .env -p 5000:5000 ai-powered-ivr-replacement
```

## API Reference

### `POST /setup`

```bash
curl -X POST http://localhost:5000/setup \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /analytics`

```bash
curl http://localhost:5000/analytics
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Webhook Endpoints

### `POST /webhooks/assistant`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
