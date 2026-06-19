## `POST /setup`

Create the media bucket (idempotent — re-running is safe).

### Response `200`

```json
{
  "status": "ready",
  "bucket": "media-cdn",
  "categories": ["ivr_prompts", "hold_music", "announcements", "voicemail_greetings"]
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/setup
```

---

## `POST /upload`

Upload a media file. The client sends the bytes directly as `multipart/form-data`, so the server never fetches an arbitrary URL (no SSRF surface).

### Request — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | `file` | **yes** | The media file bytes |
| `name` | `string` | **yes** | Object name (stored as `<category>/<name>`) |
| `category` | `string` | no | One of `ivr_prompts`, `hold_music`, `announcements`, `voicemail_greetings` (default `ivr_prompts`) |

### Response `200`

```json
{
  "status": "uploaded",
  "key": "ivr_prompts/welcome-prompt.mp3",
  "category": "ivr_prompts",
  "url": "https://us-central-1.telnyxcloudstorage.com/media-cdn/ivr_prompts/welcome-prompt.mp3?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=3600&..."
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/upload \
  -F file=@welcome-prompt.mp3 \
  -F name=welcome-prompt.mp3 \
  -F category=ivr_prompts
```

---

## `GET /media`

List stored media, optionally filtered to one category.

### Query parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | `string` | no | Filter to a single category prefix |

### Response `200`

```json
{
  "media": [
    {
      "key": "ivr_prompts/welcome-prompt.mp3",
      "size_bytes": 48213,
      "last_modified": "2026-06-18T14:30:00+00:00"
    }
  ],
  "count": 1
}
```

**Try it:**

```bash
curl "http://localhost:5000/media?category=ivr_prompts"
```

---

## `GET /media/<category>/<name>`

Return a presigned playback URL for a single object. Responds `404` if the object does not exist.

### Response `200`

```json
{
  "key": "ivr_prompts/welcome-prompt.mp3",
  "url": "https://us-central-1.telnyxcloudstorage.com/media-cdn/ivr_prompts/welcome-prompt.mp3?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=3600&...",
  "expires_in": 3600
}
```

**Try it:**

```bash
curl http://localhost:5000/media/ivr_prompts/welcome-prompt.mp3
```

---

## `GET /ivr-config`

Presigned URLs for the `ivr_prompts` and `hold_music` sets, ready to use in a call flow.

### Response `200`

```json
{
  "ivr_prompts": [
    "https://us-central-1.telnyxcloudstorage.com/media-cdn/ivr_prompts/welcome-prompt.mp3?X-Amz-..."
  ],
  "hold_music": [
    "https://us-central-1.telnyxcloudstorage.com/media-cdn/hold_music/jazz-loop.mp3?X-Amz-..."
  ],
  "usage": "Use these presigned URLs in a TeXML <Play> verb or Call Control playback_audio command."
}
```

**Try it:**

```bash
curl http://localhost:5000/ivr-config
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "bucket": "media-cdn",
  "endpoint": "https://us-central-1.telnyxcloudstorage.com"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Responses use these `status` values: `ready` (setup), `uploaded` (upload), `ok` (health).

## Error Handling

All endpoints return JSON. On error:

```json
{"error": "Description of what went wrong"}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing `file`/`name` fields, or invalid category |
| `404` | Object not found (`GET /media/<category>/<name>`) |
| `502` | Upstream Cloud Storage (S3) error |
