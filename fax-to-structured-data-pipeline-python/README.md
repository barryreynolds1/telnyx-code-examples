# Fax-to-Structured-Data Pipeline — receive faxes, AI extracts structured data (invoices, orders, prescriptions) into JSON.

Fax-to-Structured-Data Pipeline — receive faxes, AI extracts structured data (invoices, orders, prescriptions) into JSON.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |
| MMS Media | `via Messaging API` | [docs](https://developers.telnyx.com/docs/messaging) |

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
docker build -t fax-to-structured-data-pipeline .
docker run --env-file .env -p 5000:5000 fax-to-structured-data-pipeline
```

## API Reference

### `POST /extract`

```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{
  "text": "Hello, this is a test",
  "type": "auto"
}'
```

### `GET /faxes`

Returns all faxes.

```bash
curl http://localhost:5000/faxes
```

### `GET /extracted`

Returns all extracted.

```bash
curl http://localhost:5000/extracted
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

### `POST /webhooks/fax`

Receives external webhook events.

## Resources

- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [MMS Media](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
