# Edge MCP Server Deploy — deploy an MCP (Model Context Protocol) server to Telnyx edge for AI tool hosting.

Edge MCP Server Deploy — deploy an MCP (Model Context Protocol) server to Telnyx edge for AI tool hosting.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Messaging API | `POST /v2/messages` | [docs](https://developers.telnyx.com/docs/messaging) |
| Call Control API | `POST /v2/calls` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Number Lookup API | `GET /v2/number_lookup/{number}` | [docs](https://developers.telnyx.com/docs/numbers) |

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t edge-mcp-server-deploy .
docker run --env-file .env -p 5000:5000 edge-mcp-server-deploy
```

## API Reference

### `GET /mcp/tools`

Returns all tools.

```bash
curl http://localhost:5000/mcp/tools
```

### `POST /mcp/tools/register`

```bash
curl -X POST http://localhost:5000/mcp/tools/register \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Doe",
  "description": "value",
  "input_schema": "value"
}'
```

### `POST /mcp/call`

```bash
curl -X POST http://localhost:5000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
  "tool": "value",
  "params": "value"
}'
```

### `GET /mcp/deploy-info`

```bash
curl http://localhost:5000/mcp/deploy-info
```

### `GET /calls`

Returns all calls.

```bash
curl http://localhost:5000/calls
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [Messaging API](https://developers.telnyx.com/docs/messaging)
- [Call Control API](https://developers.telnyx.com/docs/voice/call-control)
- [Number Lookup API](https://developers.telnyx.com/docs/numbers)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
