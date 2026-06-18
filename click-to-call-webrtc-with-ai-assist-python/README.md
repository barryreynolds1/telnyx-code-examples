# Click-to-Call WebRTC with AI Assist — browser-based calling with real-time AI coaching sidebar.

Click-to-Call WebRTC with AI Assist — browser-based calling with real-time AI coaching sidebar.

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
| `WEBRTC_CREDENTIAL_ID` | string | `-` | **yes** | webrtc credential id |
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
docker build -t click-to-call-webrtc-with-ai-assist .
docker run --env-file .env -p 5000:5000 click-to-call-webrtc-with-ai-assist
```

## API Reference

### `GET /`

```bash
curl http://localhost:5000/
```

### `POST /webrtc/token`

```bash
curl -X POST http://localhost:5000/webrtc/token \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /coaching`

```bash
curl -X POST http://localhost:5000/coaching \
  -H "Content-Type: application/json" \
  -d '{
  "transcript": "value"
}'
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
