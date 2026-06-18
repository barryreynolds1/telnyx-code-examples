# Production-ready Flask application for cloning AI Assistants via Telnyx.

Production-ready Flask application for cloning AI Assistants via Telnyx.

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
docker build -t clone-ai-assistant .
docker run --env-file .env -p 5000:5000 clone-ai-assistant
```

## API Reference

### `GET /assistants/<assistant_id>`

```bash
curl http://localhost:5000/assistants/<assistant_id>
```

### `POST /assistants/<assistant_id>/clone`

```bash
curl -X POST http://localhost:5000/assistants/<assistant_id>/clone \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "instructions": "value"
}'
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
