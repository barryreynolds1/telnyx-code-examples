# AI Assistant Knowledge Base

## What Does This Example Do?

AI Assistant with document knowledge base for context-aware Q&A. Upload docs, auto-chunk, embed with Telnyx, and ask questions with source citations.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-assistant-knowledge-base-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| Inference | RAG + embeddings |
| AI Assistants | Knowledge-grounded answers |

## Complete Code

See [app.py](./app.py) for the full implementation.
