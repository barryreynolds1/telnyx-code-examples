## `POST /commercials/generate`

Generate commercial.

### Request

```json
{
  "product": "product_value",
  "audience": "general consumers",
  "tone": "professional",
  "length": "30s",
  "cta": "cta_value",
  "client_phone": "+12125559999",
  "script": "script_value",
  "variation": "?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product` | `string` | no | Product |
| `audience` | `string` | no | Audience |
| `tone` | `string` | no | Tone |
| `length` | `string` | no | Length |
| `cta` | `string` | no | Cta |
| `client_phone` | `string` | no | Client phone |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/commercials/generate \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `GET /commercials/<campaign_id>`

Get a specific campaign by ID.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/commercials/example-id
```

---

## `GET /commercials`

List all campaigns.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/commercials
```

---

## `GET /options`

List all options.

### Response `200`

```json
{
  "spot_lengths": "example-value",
  "tones": "example-value"
}
```

**Try it:**

```bash
curl http://localhost:5000/options
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "total_campaigns": "example-value",
  "version": "1.0.0"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `complete`, `failed`, `ok`, `rendering`, `writing`

## Error Handling

All endpoints return JSON. On error:

```json
{"error": "Description of what went wrong"}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
