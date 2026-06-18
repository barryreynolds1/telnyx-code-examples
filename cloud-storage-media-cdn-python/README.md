# Cloud Storage Media CDN — use Telnyx Cloud Storage as a CDN for IVR prompts, hold music, and voice assets.

Cloud Storage Media CDN — use Telnyx Cloud Storage as a CDN for IVR prompts, hold music, and voice assets.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Cloud Storage API | `S3-compatible` | [docs](https://developers.telnyx.com/docs/storage) |
| MMS Media | `via Messaging API` | [docs](https://developers.telnyx.com/docs/messaging) |

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
docker build -t cloud-storage-media-cdn .
docker run --env-file .env -p 5000:5000 cloud-storage-media-cdn
```

## API Reference

### `POST /setup`

```bash
curl -X POST http://localhost:5000/setup \
  -H "Content-Type: application/json" \
  -d '{}'
```

### `POST /upload`

```bash
curl -X POST http://localhost:5000/upload \
  -H "Content-Type: application/json" \
  -d '{
  "category": "ivr_prompts",
  "name": "Jane Doe",
  "url": "value"
}'
```

### `GET /media`

Returns all media.

```bash
curl http://localhost:5000/media
```

### `GET /media/<category>/<name>`

```bash
curl http://localhost:5000/media/<category>/<name>
```

### `GET /ivr-config`

```bash
curl http://localhost:5000/ivr-config
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

- [Cloud Storage API](https://developers.telnyx.com/docs/storage)
- [MMS Media](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
