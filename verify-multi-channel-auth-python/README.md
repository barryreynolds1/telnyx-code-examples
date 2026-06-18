# Verify Multi-Channel Auth

## What Does This Example Do?

Multi-channel verification cascade: SMS first, escalate to voice call if no response, then WhatsApp. Automatic channel fallback for maximum reach.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/verify-multi-channel-auth-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Verify API | Multi-channel 2FA |
| SMS + Voice + WhatsApp | Cascading delivery |

## Complete Code

See [app.py](./app.py) for the full implementation.
