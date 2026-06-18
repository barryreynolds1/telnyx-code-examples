# Full-Stack AI Contact Center

## What Does This Example Do?

Complete contact center in one file: IVR menu, queue routing, AI agent assist while waiting, call recording, and live analytics dashboard.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/full-stack-ai-contact-center-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Voice API | IVR + call routing |
| Inference | AI agent assist |
| Recording | Call capture |
| Analytics | Live dashboard |

## Complete Code

See [app.py](./app.py) for the full implementation.
