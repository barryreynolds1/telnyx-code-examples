## `POST /buckets`

Create the archive bucket. Idempotent — if you already own the bucket it returns success.

### Response `200`

```json
{
  "status": "ready",
  "bucket": "call-archive"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/buckets
```

---

## `GET /buckets`

List the buckets in your Telnyx Cloud Storage account.

### Response `200`

```json
{
  "buckets": ["call-archive"]
}
```

**Try it:**

```bash
curl http://localhost:5000/buckets
```

---

## `POST /archive`

Download a recording from its Telnyx URL and store it in the bucket with its metadata.

### Request

```json
{
  "recording_url": "https://api.telnyx.com/v2/recordings/abc123/download.mp3",
  "call_id": "call-abc123",
  "metadata": {"agent": "alice", "campaign": "summer-sale"}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recording_url` | `string` | **yes** | Must be an `https` Telnyx URL (`telnyx.com` or `*.telnyx.com`). Any other host is rejected. |
| `call_id` | `string` | no | Identifier used for the object key. Defaults to `call-<unix-timestamp>`. |
| `metadata` | `object` | no | Arbitrary key/value metadata stored on the S3 object (coerced to strings). |

### Response `200`

```json
{
  "status": "archived",
  "entry": {
    "call_id": "call-abc123",
    "object_key": "2026/06/18/call-abc123.mp3",
    "bucket": "call-archive",
    "size_bytes": 184320,
    "metadata": {"agent": "alice", "campaign": "summer-sale"},
    "archived_at": "2026-06-18T14:30:00Z"
  }
}
```

### Response `400`

```json
{
  "error": "recording_url must be an https Telnyx URL"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/archive \
  -H "Content-Type: application/json" \
  -d '{"recording_url": "https://api.telnyx.com/v2/recordings/abc123/download.mp3", "call_id": "call-abc123", "metadata": {"agent": "alice"}}'
```

---

## `POST /webhooks/recording`

Receives Telnyx Call Control webhooks. On `call.recording.saved` it reads `data.payload.recording_urls.mp3` and queues the recording's metadata.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/webhooks/recording \
  -H "Content-Type: application/json" \
  -d '{"data": {"event_type": "call.recording.saved", "payload": {"call_control_id": "v3:abc", "recording_urls": {"mp3": "https://api.telnyx.com/v2/recordings/abc123/download.mp3"}, "recording_duration_millis": 42000}}}'
```

---

## `GET /archive`

List archived recordings, optionally filtered by `date` (`YYYY/MM/DD`, matched against the object key). Returns the most recent 50.

### Query parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | `string` | no | Filter by `YYYY/MM/DD` matched against the object key. |

### Response `200`

```json
{
  "recordings": [
    {
      "call_id": "call-abc123",
      "object_key": "2026/06/18/call-abc123.mp3",
      "bucket": "call-archive",
      "size_bytes": 184320,
      "metadata": {"agent": "alice"},
      "archived_at": "2026-06-18T14:30:00Z"
    }
  ],
  "total": 1
}
```

**Try it:**

```bash
curl "http://localhost:5000/archive?date=2026/06/18"
```

---

## `GET /archive/search`

Full-text search across the metadata index. `q` is matched case-insensitively against each entry's JSON. Returns up to 20 results.

### Query parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | `string` | no | Search term. |

### Response `200`

```json
{
  "results": [
    {
      "call_id": "call-abc123",
      "object_key": "2026/06/18/call-abc123.mp3",
      "bucket": "call-archive",
      "size_bytes": 184320,
      "metadata": {"agent": "alice"},
      "archived_at": "2026-06-18T14:30:00Z"
    }
  ],
  "query": "alice"
}
```

**Try it:**

```bash
curl "http://localhost:5000/archive/search?q=alice"
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "archived": 1,
  "bucket": "call-archive"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Archive entries and responses use these status values: `archived`, `queued`, `ready`, `ok`

## Error Handling

All endpoints return JSON. On error:

```json
{
  "error": "recording_url must be an https Telnyx URL"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing/invalid body, missing `recording_url`, or a non-Telnyx `recording_url` |
| `502` | Upstream error — recording download failed or a Cloud Storage (S3) operation failed |
