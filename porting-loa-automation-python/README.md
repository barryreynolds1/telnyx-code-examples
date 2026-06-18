# Porting LOA Automation

## What Does This Example Do?

Automate Letter of Authorization generation and porting order submission. Generate LOAs from templates, check portability, submit orders.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/porting-loa-automation-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Porting API | Automated porting |
| Number Portability | Pre-port validation |

## Complete Code

See [app.py](./app.py) for the full implementation.
