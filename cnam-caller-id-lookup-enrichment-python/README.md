# CNAM Caller ID Lookup Enrichment — look up CNAM for inbound callers, enrich CRM records with caller identity.

CNAM Caller ID Lookup Enrichment — look up CNAM for inbound callers, enrich CRM records with caller identity.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Number Lookup API | `GET /v2/number_lookup/{number}` | [docs](https://developers.telnyx.com/docs/numbers) |

## Webhook Events Handled

```
call.initiated
```

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
docker build -t cnam-caller-id-lookup-enrichment .
docker run --env-file .env -p 5000:5000 cnam-caller-id-lookup-enrichment
```

## API Reference

### `GET /lookup/<number>`

```bash
curl http://localhost:5000/lookup/<number>
```

### `POST /lookup/batch`

```bash
curl -X POST http://localhost:5000/lookup/batch \
  -H "Content-Type: application/json" \
  -d '{
  "numbers": "+12125551234"
}'
```

### `GET /enrichments`

Returns all enrichments.

```bash
curl http://localhost:5000/enrichments
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

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.initiated`

Example payload:

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:abc-123",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876"
  }
}
```

## Resources

- [Number Lookup API](https://developers.telnyx.com/docs/numbers)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
