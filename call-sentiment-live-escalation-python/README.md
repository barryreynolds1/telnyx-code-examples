# Call Sentiment Live Escalation — monitor call transcripts in real-time. When negative sentiment or distress is detected, auto-escalate to a supervisor.

Call Sentiment Live Escalation — monitor call transcripts in real-time. When negative sentiment or distress is detected, auto-escalate to a supervisor.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |
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
| `SUPERVISOR_NUMBER` | string | `+E.164` | **yes** | supervisor number |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t call-sentiment-live-escalation .
docker run --env-file .env -p 5000:5000 call-sentiment-live-escalation
```

## API Reference

### `POST /monitor`

```bash
curl -X POST http://localhost:5000/monitor \
  -H "Content-Type: application/json" \
  -d '{
  "call_id": "abc-123",
  "agent": "value",
  "customer": "value"
}'
```

### `POST /transcript`

```bash
curl -X POST http://localhost:5000/transcript \
  -H "Content-Type: application/json" \
  -d '{
  "call_id": "abc-123",
  "text": "Hello, this is a test",
  "speaker": "customer"
}'
```

### `GET /calls/<call_id>/sentiment`

```bash
curl http://localhost:5000/calls/<call_id>/sentiment
```

### `GET /escalations`

Returns all escalations.

```bash
curl http://localhost:5000/escalations
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

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
