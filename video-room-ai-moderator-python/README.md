# Video Room AI Moderator

## What Does This Example Do?

Create video rooms with AI-powered chat moderation. Detects profanity, harassment, spam, and threats with severity scoring and auto-actions.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/video-room-ai-moderator-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Video Rooms | Room creation + management |
| Inference | Content moderation |

## Complete Code

See [app.py](./app.py) for the full implementation.
