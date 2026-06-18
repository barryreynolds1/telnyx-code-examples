# Edge Compute Webhook Proxy

Local dev server for testing webhook routing logic before deploying to Telnyx Edge. Includes the Edge function source and deployment instructions.

## Webhook Events Handled

```
call.initiated
call.answered
call.speak.ended
call.gather.ended
call.hangup
message.received
```

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `VOICE_HANDLER_URL` | string | `https://...` | **yes** | voice handler url |
| `MESSAGE_HANDLER_URL` | string | `https://...` | **yes** | message handler url |
| `DEFAULT_HANDLER_URL` | string | `https://...` | **yes** | default handler url |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t edge-compute-webhook-proxy .
docker run --env-file .env -p 5000:5000 edge-compute-webhook-proxy
```

## API Reference

### `GET /edge-source`

```bash
curl http://localhost:5000/edge-source
```

### `GET /routes`

Returns all routes.

```bash
curl http://localhost:5000/routes
```

### `GET /stats`

Dashboard/analytics view.

```bash
curl http://localhost:5000/stats
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

### `POST /webhook`

Receives external webhook events.

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
