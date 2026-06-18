# Billing Anomaly Detector

## What Does This Example Do?

Monitor usage and billing for anomalies. Detect cost spikes, volume drops, and expensive calls. Alert via webhook when thresholds exceeded.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/billing-anomaly-detector-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Reporting API | Usage monitoring |
| Balance API | Cost tracking |

## Complete Code

See [app.py](./app.py) for the full implementation.
