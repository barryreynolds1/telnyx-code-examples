## `GET /sip/connections`

List all connections.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/sip/connections
```

---

## `POST /sip/connections`

Create a new connection.

### Request

```json
{
  "name": "Jane Smith",
  "codecs": [
    "G.711"
  ],
  "username": "Jane Smith",
  "password": "password_value",
  "sip_endpoint": "sip_endpoint_value"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | **yes** | Display name or label |
| `codecs` | `string` | no | Codecs |
| `username` | `string` | **yes** | Username |
| `password` | `string` | **yes** | Password |
| `sip_endpoint` | `string` | **yes** | Sip endpoint |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/sip/connections \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `GET /sip/connections/<connection_id>`

Get a specific connection by ID.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/sip/connections/example-id
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
