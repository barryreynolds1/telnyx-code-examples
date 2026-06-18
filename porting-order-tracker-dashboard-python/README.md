# Porting Order Tracker Dashboard

## What Does This Example Do?

Submit and track number porting orders with real-time status webhook updates. Dashboard view with status breakdowns.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/porting-order-tracker-dashboard-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Porting API | Order submission + tracking |
| Webhooks | Status notifications |

## Complete Code

See [app.py](./app.py) for the full implementation.
