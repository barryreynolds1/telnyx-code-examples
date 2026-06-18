## `POST /orders`

Create a new order.

### Request

```json
{
  "order_id": "f\"ORD-{int(time.time(",
  "customer_phone": "+12125559999"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | `string` | no | Order identifier |
| `customer_phone` | `string` | **yes** | Customer phone |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `PUT /orders/<order_id>/status`

Update status.

### Request

```json
{
  "statuss": [
    {
      "id": "abc-123",
      "status": "active",
      "created_at": "2026-06-18T21:00:00Z"
    }
  ],
  "total": 1
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | `string` | **yes** | Current status value |
| `tracking_number` | `string` | **yes** | Tracking number |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X PUT http://localhost:5000/orders/example-id/status \
  -H "Content-Type: application/json" \
  -d '{"statuss": [{"id": "abc-123", "status": "active", "created_at": "2026-06-18T21:00:00Z"}], "total": 1}'
```

---

## `POST /webhooks/messaging`

Receives Telnyx Messaging webhook events. Called automatically by Telnyx for inbound messages — do not call directly.

---

**Try it:**

```bash
curl -X POST http://localhost:5000/webhooks/messaging
```

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "orders": "<string>"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `confirmed`, `created`, `ignored`, `ok`, `responded`

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
