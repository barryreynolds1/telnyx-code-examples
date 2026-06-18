# Edge MCP Server Deploy

## What Does This Example Do?

Deploy a Model Context Protocol (MCP) server to Telnyx edge for AI tool hosting. Exposes SMS, voice, lookup, and number search as MCP tools.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/edge-mcp-server-deploy-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Edge Compute | MCP server hosting |
| MCP | AI tool protocol |
| Voice + SMS | Tool execution |

## Complete Code

See [app.py](./app.py) for the full implementation.
