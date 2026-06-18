# AI Assistant Multi-Tool

## What Does This Example Do?

AI Assistant with function-calling tools: CRM lookup, order tracking, and appointment booking. AI decides when to call each tool.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-assistant-multi-tool-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Inference | Function calling |
| AI Assistants | Tool-equipped agents |

## Complete Code

See [app.py](./app.py) for the full implementation.
