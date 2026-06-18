# Migrate from Vapi — import Vapi voice agents to Telnyx AI Assistants with voice, prompt, and tool configuration mapping.

Migrate from Vapi — import Vapi voice agents to Telnyx AI Assistants with voice, prompt, and tool configuration mapping.

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → process → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `VAPI_API_KEY` | string | `token` | **yes** | vapi api key |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Webhook URL

Expose with [ngrok](https://ngrok.com): `ngrok http 5000`

Configure in [Telnyx Portal](https://portal.telnyx.com):

- **Call Control App** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/voice`

### Docker

```bash
docker build -t migrate-from-vapi .
docker run --env-file .env -p 5000:5000 migrate-from-vapi
```

## API Reference

### `GET /audit/vapi`

```bash
curl http://localhost:5000/audit/vapi
```

### `POST /migrate/agent`

```bash
curl -X POST http://localhost:5000/migrate/agent \
  -H "Content-Type: application/json" \
  -d '{
  "vapi_agent": "value"
}'
```

### `GET /mapping/voices`

```bash
curl http://localhost:5000/mapping/voices
```

### `GET /mapping/models`

```bash
curl http://localhost:5000/mapping/models
```

### `GET /migration-log`

```bash
curl http://localhost:5000/migration-log
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

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
