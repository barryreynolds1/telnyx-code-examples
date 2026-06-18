# Branded Caller ID Manager

## What Does This Example Do?

Register and manage branded calling profiles with STIR/SHAKEN attestation. Increase answer rates by displaying your verified business name on outbound calls.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/branded-caller-id-manager-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Branded Calling | CNAM registration + verification |
| Phone Numbers | Caller ID configuration |

## Complete Code

See [app.py](./app.py) for the full implementation.
