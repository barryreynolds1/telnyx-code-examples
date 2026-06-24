# API Reference — OTP 2FA

All endpoints accept and return JSON. Base URL in local development: `http://localhost:5000`.

---

## `POST /auth/2fa/request-otp`

Submit data to `/auth/2fa/request-otp`.

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
curl -X POST http://localhost:5000/auth/2fa/request-otp \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## `POST /auth/2fa/verify-otp`

Submit data to `/auth/2fa/verify-otp`.

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
curl -X POST http://localhost:5000/auth/2fa/verify-otp \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## `POST /auth/2fa/resend-otp`

Submit data to `/auth/2fa/resend-otp`.

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
curl -X POST http://localhost:5000/auth/2fa/resend-otp \
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
