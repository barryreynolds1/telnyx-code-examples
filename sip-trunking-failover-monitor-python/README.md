# SIP Trunking Failover Monitor — health-check SIP connections, auto-failover, SMS alerts.

SIP Trunking Failover Monitor — health-check SIP connections, auto-failover, SMS alerts.

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
| `ALERT_NUMBER` | string | `+E.164` | **yes** | alert number |
| `PRIMARY_SIP_CONNECTION_ID` | string | `-` | **yes** | primary sip connection id |
| `BACKUP_SIP_CONNECTION_ID` | string | `-` | **yes** | backup sip connection id |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t sip-trunking-failover-monitor .
docker run --env-file .env -p 5000:5000 sip-trunking-failover-monitor
```

## API Reference

### `POST /check`

```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /status`

Update record status.

```bash
curl http://localhost:5000/status
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
