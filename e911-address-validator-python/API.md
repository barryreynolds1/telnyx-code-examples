## `POST /e911/validate`

Validate address.

### Request

```json
{
  "street": "street_value",
  "street2": "street2_value",
  "city": "New York",
  "state": "NY",
  "zip": "10001",
  "country": "US",
  "business_name": ", timeout=10"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `street` | `string` | **yes** | Street |
| `street2` | `string` | no | Street2 |
| `city` | `string` | **yes** | City |
| `state` | `string` | **yes** | State |
| `zip` | `string` | **yes** | Zip |
| `country` | `string` | no | Country |
| `business_name` | `string` | no | Business name |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/e911/validate \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `POST /e911/assign`

Assign e911.

### Request

```json
{
  "street": "street_value",
  "street2": "street2_value",
  "city": "New York",
  "state": "NY",
  "zip": "10001",
  "country": "US",
  "business_name": ", timeout=10"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_number` | `string` | **yes** | Phone number |
| `address_id` | `string` | **yes** | Address id |

### Response `200`

```json
{
  "status": "ok"
}
```

**Try it:**

```bash
curl -X POST http://localhost:5000/e911/assign \
  -H "Content-Type: application/json" \
  -d '<see Request example above>'
```

---

## `GET /e911/addresses`

List all addresses.

### Response `200`

```json
{
  "addresses": []
}
```

**Try it:**

```bash
curl http://localhost:5000/e911/addresses
```

---

## `GET /health`

Health check and service status.

### Response `200`

```json
{
  "status": "ok",
  "addresses": "<string>"
}
```

**Try it:**

```bash
curl http://localhost:5000/health
```

---

## Status Values

Records use these status values: `assigned`, `ok`

## Error Handling

All endpoints return JSON. On error:

```json
{
  "status": "ok",
  "addresses": "example-value"
}
```

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request — missing or invalid fields |
| `500` | Server error |
