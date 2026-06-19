# Contributing to Telnyx Code Examples

## Adding a new example

1. Create a directory: `your-example-name-python/`
2. Include these files:
   - `app.py` -- working application code
   - `README.md` -- with YAML frontmatter (see any existing example)
   - `GUIDE.md` -- tutorial walkthrough
   - `API.md` -- endpoint reference
   - `.env.example` -- all required environment variables
   - `requirements.txt` -- Python dependencies

3. Verify:
   ```bash
   python3 -m py_compile your-example-name-python/app.py
   ```

4. Open a PR with a clear description of what the example does and which Telnyx products it uses.

## README frontmatter

Every README must start with YAML frontmatter:

```yaml
---
name: your-example-name
title: "Your Example Title"
description: "One-line description of what it does."
language: python
framework: flask
telnyx_products: [Voice, AI Inference, Messaging]
integrations: [Slack]
channel: [voice, sms]
---
```

## Code standards

- Use `os.getenv()` for all configuration (never hardcode keys)
- Add `timeout=` to all `requests` calls
- Bind to `HOST` env var (default `127.0.0.1`), not `0.0.0.0`
- Use `%s` format for logger calls (not f-strings)
- Add input validation for webhook payloads
- Include a `/health` endpoint

## Questions?

Open an issue or check [developers.telnyx.com](https://developers.telnyx.com).
