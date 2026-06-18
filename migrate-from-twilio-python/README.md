# Migrate from Twilio

## What Does This Example Do?

Complete Twilio-to-Telnyx migration tool. Audit existing Twilio resources, port numbers, map webhooks, and translate code patterns.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/migrate-from-twilio-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Porting API | Number migration |
| Messaging Profiles | Config mapping |
| Voice API | Webhook translation |

## Complete Code

See [app.py](./app.py) for the full implementation.
