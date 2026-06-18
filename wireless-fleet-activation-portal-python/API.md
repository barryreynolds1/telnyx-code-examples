## `GET /sims`

List all sims.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/sims
```

---

## `POST /sims/activate`

Activate sims.

### Request

```json
{
  "sim_ids": "sims-abc123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sim_ids` | `string` | no | Sim ids |

### Response `200`

```json
{"results": null, "activated": "<string>"}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/sims/activate \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /sims/deactivate`

Deactivate sims.

### Request

```json
{
  "sim_ids": "sims-abc123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sim_ids` | `string` | no | Sim ids |

### Response `200`

```json
{"results": null}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/sims/deactivate \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `GET /activation-log`

Get a specific log by ID.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/activation-log
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "activations": "<string>"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `active`, `deactivated`, `error`, `inactive`, `ok`

## Error Handling

All endpoints return JSON. On error:

```json
{
  "log": "example-value"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
