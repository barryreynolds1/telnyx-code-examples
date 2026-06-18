# Edge Compute Webhook Proxy

## What Does This Example Do?

Deploy a webhook handler to Telnyx edge infrastructure for low-latency event processing and intelligent routing to downstream services.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/edge-compute-webhook-proxy-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Edge Compute | Serverless edge functions |
| Webhooks | Event routing + processing |

## Complete Code

See [app.py](./app.py) for the full implementation.
