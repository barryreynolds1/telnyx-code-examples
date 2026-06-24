# API Reference — MQTT Messaging

All endpoints accept and return JSON. Base URL in local development: `http://localhost:5000`.

---

## `GET /sims`

Retrieve data from `/sims`.

### Request

```json
{
  "example": "see source code for full schema"
}
```

### Response `200`

```json
{
  "status": "ok"
}
```

### Try it

```bash
curl http://localhost:5000/sims
```

---

## `GET /sims/<sim_card_id>/usage`

Retrieve data from `/sims/<sim_card_id>/usage`.

### Request

```json
{
  "example": "see source code for full schema"
}
```

### Response `200`

```json
{
  "status": "ok"
}
```

### Try it

```bash
curl http://localhost:5000/sims/<sim_card_id>/usage
```

---

## `POST /sims/<sim_card_id>/publish`

Submit data to `/sims/<sim_card_id>/publish`.

### Request

```json
{
  "example": "see source code for full schema"
}
```

### Response `200`

```json
{
  "status": "ok"
}
```

### Try it

```bash
curl -X POST http://localhost:5000/sims/<sim_card_id>/publish \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## `POST /sims/publish-all`

Submit data to `/sims/publish-all`.

### Request

```json
{
  "example": "see source code for full schema"
}
```

### Response `200`

```json
{
  "status": "ok"
}
```

### Try it

```bash
curl -X POST http://localhost:5000/sims/publish-all \
  -H "Content-Type: application/json" \
  -d '{}'
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
| `401` | Invalid API key or webhook signature |
| `429` | Rate limit exceeded |
| `500` | Server error |
| `503` | Upstream network error talking to Telnyx |
