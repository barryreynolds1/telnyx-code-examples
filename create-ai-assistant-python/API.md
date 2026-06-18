## `POST /ai/assistants`

Create assistant endpoint.

### Request

```json
{
  "name": "Jane Smith",
  "instructions": "You are a helpful agent.",
  "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
  "enabled_features": [
    "messaging"
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | **yes** | Display name or label |
| `instructions` | `string` | **yes** | Instructions |
| `model` | `string` | no | AI model name |
| `enabled_features` | `string` | no | Enabled features |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/ai/assistants \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

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
