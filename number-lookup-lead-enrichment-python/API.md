## `POST /enrich`

Enrich lead.

### Request

```json
{
  "phone_number": "+12125559999"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_number` | `string` | **yes** | Phone number |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/enrich \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /enrich/bulk`

Enrich bulk.

### Request

```json
{
  "phone_number": "+12125559999"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_numbers` | `array` | no | Phone numbers |

### Response `200`

```json
{"results": null, "total": "<string>"}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/enrich/bulk \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "enriched": "<string>"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Error Handling

All endpoints return JSON. On error:

```json
{
  "error": "invalid request body"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
