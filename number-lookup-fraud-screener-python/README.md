# Number Lookup Fraud Screener

## What Does This Example Do?

Screen inbound calls for fraud indicators using number lookup. Risk scoring based on carrier type, CNAM, porting status, and origin. Auto-blocklist.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/number-lookup-fraud-screener-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Number Lookup | Fraud risk scoring |
| Voice API | Inbound call screening |

## Complete Code

See [app.py](./app.py) for the full implementation.
