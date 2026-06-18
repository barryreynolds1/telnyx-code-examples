# Bulk Number Validation & Cleaner

## What Does This Example Do?

Validate and clean phone number lists via Telnyx Number Lookup API. Classify as mobile/landline/VoIP, check validity, identify carrier.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/bulk-number-validation-cleaner-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Number Lookup | Bulk validation |
| Reporting | List quality metrics |

## Complete Code

See [app.py](./app.py) for the full implementation.
