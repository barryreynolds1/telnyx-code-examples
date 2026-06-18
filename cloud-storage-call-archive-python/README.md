# Cloud Storage Call Archive — archive call recordings to Telnyx Cloud Storage with searchable metadata.

Cloud Storage Call Archive — archive call recordings to Telnyx Cloud Storage with searchable metadata.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Cloud Storage API | `S3-compatible` | [docs](https://developers.telnyx.com/docs/storage) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `BUCKET_NAME` | string | `-` | no | bucket name |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t cloud-storage-call-archive .
docker run --env-file .env -p 5000:5000 cloud-storage-call-archive
```

## API Reference

### `POST /buckets`

Create a new record.

```bash
curl -X POST http://localhost:5000/buckets \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `GET /buckets`

Returns all buckets.

```bash
curl http://localhost:5000/buckets
```

### `POST /archive`

```bash
curl -X POST http://localhost:5000/archive \
  -H "Content-Type: application/json" \
  -d '{
  "recording_url": "value",
  "call_id": "f\"call-{int(time.time(",
  "metadata": "value"
}'
```

### `GET /archive`

Returns all archive.

```bash
curl http://localhost:5000/archive
```

### `GET /archive/search`

```bash
curl http://localhost:5000/archive/search
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

### `POST /webhooks/recording`

Receives external webhook events.

## Resources

- [Cloud Storage API](https://developers.telnyx.com/docs/storage)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
