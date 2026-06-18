# Production-ready Flask endpoint for creating AI assistants via Telnyx.

Production-ready Flask endpoint for creating AI assistants via Telnyx.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
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
docker build -t create-ai-assistant .
docker run --env-file .env -p 5000:5000 create-ai-assistant
```

## API Reference

### `POST /ai/assistants`

Create a new record.

```bash
curl -X POST http://localhost:5000/ai/assistants \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "instructions": "value",
  "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
  "enabled_features": "[\"messaging\"]"
}'
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
