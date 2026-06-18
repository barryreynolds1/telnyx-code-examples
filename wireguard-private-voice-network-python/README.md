# WireGuard Private Voice Network

## What Does This Example Do?

Create encrypted WireGuard mesh networks for private SIP trunking. Generate peer configs and manage network topology via API.

## Prerequisites

- Python 3.8+
- Telnyx account with API key from [portal.telnyx.com](https://portal.telnyx.com)

## Quick Start

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/wireguard-private-voice-network-python
cp .env.example .env
# Edit .env with your credentials
make setup && make run
```

## Products Used

| Product | Role |
|---------|------|
| WireGuard Networking | Encrypted mesh networks |
| Private Networks | Secure SIP transport |

## Complete Code

See [app.py](./app.py) for the full implementation.
