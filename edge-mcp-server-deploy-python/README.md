---
name: edge-mcp-server-deploy
title: "Edge MCP Server Deploy"
description: "Edge MCP Server Deploy — deploy an MCP (Model Context Protocol) server to Telnyx edge for AI tool hosting."
language: python
framework: flask
telnyx_products: [SMS/MMS, Voice, Number Lookup]
---

# Edge MCP Server Deploy

Edge MCP Server Deploy — deploy an MCP (Model Context Protocol) server to Telnyx edge for AI tool hosting.

## Telnyx API Endpoints Used

- **Messaging**: `POST /v2/messages` — [API reference](https://developers.telnyx.com/api/messaging/send-message)
- **Call Control: Dial**: `POST /v2/calls` — [API reference](https://developers.telnyx.com/api/call-control/dial)
- **Number Lookup**: `GET /v2/number_lookup/{phone_number}` — [API reference](https://developers.telnyx.com/api/number-lookup/lookup)

## Architecture

```text
┌─────────────┐                        ┌──────────────────────┐
│  API Client │───────────────────────►│     Your App         │
└─────────────┘                        └──────────┬───────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Response (SMS/  │
                                          │ Voice/Webhook)  │
                                          └─────────────────┘
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Type | Example | Required | Description | Where to get it |
|----------|------|---------|----------|-------------|-----------------|
| `TELNYX_API_KEY` | `string` | `KEY...` | **yes** | Telnyx API v2 key | [→ link](https://portal.telnyx.com/api-keys) |

## Setup

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/edge-mcp-server-deploy-python
cp .env.example .env    # ← fill in your credentials
pip install -r requirements.txt
python app.py           # starts on http://localhost:5000
```

### Docker

```bash
docker build -t edge-mcp-server-deploy .
docker run --env-file .env -p 5000:5000 edge-mcp-server-deploy
```

## API Reference

### `GET /mcp/tools`

Returns all tools.

**Request:**

```bash
curl http://localhost:5000/mcp/tools
```

**Response:**

```json
{
  "tools": [
    "..."
  ]
}
```

### `POST /mcp/tools/register`

Handles `POST /mcp/tools/register`.

**Request:**

```bash
curl -X POST http://localhost:5000/mcp/tools/register \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "description": "Customer reported issue with service",
  "input_schema": "example_value"
}'
```

**Response:**

```json
{
  "status": "ok",
  "tool": "..."
}
```

### `POST /mcp/call`

Handles `POST /mcp/call`.

**Request:**

```bash
curl -X POST http://localhost:5000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
  "tool": "example_value",
  "params": "example_value"
}'
```

**Response:**

```json
{
  "result": "..."
}
```

### `GET /mcp/deploy-info`

Handles `GET /mcp/deploy-info`.

**Request:**

```bash
curl http://localhost:5000/mcp/deploy-info
```

**Response:**

```json
{
  "deploy_command": "...",
  "note": "...",
  "tools_count": 3
}
```

### `GET /calls`

Returns all calls.

**Request:**

```bash
curl http://localhost:5000/calls
```

**Response:**

```json
{
  "calls": "..."
}
```

### `GET /health`

Returns service health and operational metrics.

**Request:**

```bash
curl http://localhost:5000/health
```

**Response:**

```json
{
  "status": "ok"
}
```

## Resources

- [Messaging — API Reference](https://developers.telnyx.com/api/messaging/send-message)
- [Call Control: Dial — API Reference](https://developers.telnyx.com/api/call-control/dial)
- [Number Lookup — API Reference](https://developers.telnyx.com/api/number-lookup/lookup)
- [Telnyx Developer Documentation](https://developers.telnyx.com)
- [Telnyx Portal (dashboard)](https://portal.telnyx.com)
