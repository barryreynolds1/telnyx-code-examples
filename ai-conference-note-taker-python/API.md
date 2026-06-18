## `POST /join`

Join meeting.

### Request

```json
{
  "dial_number": "+12125559999",
  "participants": "participants_value",
  "call_control_id": "call_control-abc123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dial_number` | `string` | **yes** | Dial number |
| `participants` | `array` | no | List of participant phone numbers |
| `call_control_id` | `string` | **yes** | Call control id |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/join \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /webhooks/voice`

Receives Telnyx Call Control webhook events. Called automatically by Telnyx during calls — do not call directly.

---

**Try it:**

```bash
curl -X POST http://localhost:5000/webhooks/voice
```

## `GET /meetings`

List all meetings.

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl http://localhost:5000/meetings
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "active_meetings": "example-value",
  "completed": "example-value"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `event_received`, `joining`, `meeting_ended`, `ok`, `recording`, `transcribing`

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
