# Cloud Storage Call Archive

## What Does This Example Do?

Archive call recordings to Telnyx Cloud Storage with searchable metadata. Auto-archive via recording webhooks with date-based organization.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/cloud-storage-call-archive-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Cloud Storage | Recording archival |
| Webhooks | Auto-archive triggers |
| Voice API | Recording capture |

## Complete Code

See [app.py](./app.py) for the full implementation.
