# CNAM Caller ID Lookup Enrichment

## What Does This Example Do?

Look up CNAM (Caller Name) for inbound callers and enrich CRM records. Batch lookup support for cleaning contact lists.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/cnam-caller-id-lookup-enrichment-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Number Lookup | CNAM + carrier identification |
| Webhooks | Real-time inbound enrichment |

## Complete Code

See [app.py](./app.py) for the full implementation.
