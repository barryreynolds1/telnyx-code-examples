## `POST /prompts/generate`

Generate prompts.

### Request

```json
{
  "business_name": "Jane Smith",
  "business_type": "business_type_value",
  "hours": "Monday-Friday 9am-5pm",
  "departments": [
    "Sales",
    "Support",
    "Billing"
  ],
  "voice": "nova",
  "prompt_types": "list(PROMPT_TYPES.keys(",
  "script": "script_value",
  "type": "inbound",
  "estimated_seconds": "estimated_seconds_value"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `business_name` | `string` | no | Business name |
| `business_type` | `string` | no | Business type |
| `hours` | `string` | no | Hours |
| `departments` | `string` | no | Departments |
| `voice` | `string` | no | TTS voice identifier |
| `prompt_types` | `string` | no | Prompt types |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/prompts/generate \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /prompts/<set_id>/preview`

Preview prompt.

### Request

```json
{
  "phone": "+12125559999",
  "type": "type-value"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone` | `string` | no | Phone number in E.164 format (e.g., `+12125551234`) |
| `type` | `string` | no | Type |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/prompts/example-id/preview \
  -H "Content-Type: application/json" \
  -d '{"phone": "+12125559999", "type": "type-value"}'
```

---

## `POST /webhooks/voice`

Receives Telnyx Call Control webhook events. Called automatically by Telnyx during calls — do not call directly.

---

**Try it:**

```bash
curl -X POST http://localhost:5000/webhooks/voice
```

## `GET /prompts/<set_id>`

Get prompt set.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/prompts/example-id
```

---

## `GET /prompt-types`

Get prompt types.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/prompt-types
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "types": "example-value"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `calling`, `complete`, `failed`, `ok`, `rendering`, `writing`

## Error Handling

All endpoints return JSON. On error:

```json
{
  "status": "ok",
  "total_sets": "example-value",
  "version": "1.0.0"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
