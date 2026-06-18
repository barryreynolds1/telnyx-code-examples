## `POST /rooms`

Create a new room.

### Request

```json
{
  "agenda": "agenda_value",
  "duration_minutes": 30,
  "name": "f\"meeting-{int(time.time(",
  "max_participants": 10,
  "id": "id_value"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agenda` | `array` | no | Agenda |
| `duration_minutes` | `string` | no | Duration minutes |
| `name` | `string` | no | Display name or label |
| `max_participants` | `string` | no | Max participants |
| `id` | `string` | **yes** | Id |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/rooms \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /rooms/<room_id>/start`

Start meeting.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/rooms/example-id/start \
  -H "Content-Type: application/json" \
  -d '{"error": "Room not found"}'
```

---

## `GET /rooms/<room_id>/status`

Meeting status.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/rooms/example-id/status
```

---

## `POST /rooms/<room_id>/next`

Next topic.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/rooms/example-id/next \
  -H "Content-Type: application/json" \
  -d '{"error": "Room not found"}'
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "rooms": "<string>"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `active`, `all_topics_completed`, `completed`, `no_active_topic`, `ok`, `pending`, `started`

## Error Handling

All endpoints return JSON. On error:

```json
{
  "status": "ok",
  "rooms": "example-value"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
