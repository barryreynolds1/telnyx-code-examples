# CDR Usage Analytics Dashboard

## What Does This Example Do?

Pull Call Detail Records, build usage analytics with cost breakdowns, daily trends, and top-number analysis.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/cdr-usage-analytics-dashboard-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Reporting API | CDR retrieval |
| Analytics | Usage + cost analysis |

## Complete Code

See [app.py](./app.py) for the full implementation.
