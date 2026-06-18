# Global IP Failover Monitor

## What Does This Example Do?

Monitor Global IP endpoints across regions with health checks. Auto-failover to healthy endpoints when primary goes down. Track uptime metrics.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/global-ip-failover-monitor-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Global IP | Multi-region IP management |
| Health Checks | Endpoint monitoring + failover |

## Complete Code

See [app.py](./app.py) for the full implementation.
