# Media Stream Custom Audio Mixer

## What Does This Example Do?

Mix custom audio into live calls via WebSocket-based media streaming. Inject background music, sound effects, or announcements.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/media-stream-custom-audio-mixer-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Media Streaming | WebSocket audio streams |
| Voice API | Live call audio injection |

## Complete Code

See [app.py](./app.py) for the full implementation.
