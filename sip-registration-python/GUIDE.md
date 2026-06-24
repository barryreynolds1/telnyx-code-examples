# SIP Registration with Python and Flask

Build a production-ready Flask application that manages SIP connections and handles registration with Telnyx.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Python Server      │  receives request
  └─────────┬──────────┘
        │  Telnyx API call
        ▼
  ┌────────────────────┐
  │  Telnyx SIP Trunking│  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **SIP Trunking** — [Documentation](https://developers.telnyx.com/docs/sip-trunking)

## Prerequisites

- Python 3.8 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Basic understanding of SIP (Session Initiation Protocol) concepts.
- A SIP client (softphone, PBX, or SBC) for testing registration.
- pip (Python package manager).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sip-registration-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `FLASK_DEBUG` | your_flask_debug_here |
| `SIP_DOMAIN` | your_sip_domain_here |

## Step 2: Understand the Code

The main application logic lives in `app.py`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/sip/connections` | API endpoint |
| `GET` | `/sip/connections/<connection_id>` | API endpoint |
| `GET` | `/sip/connections` | API endpoint |
| `GET` | `/` | API endpoint |

## Step 3: Run It

```bash
python app.py
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl http://localhost:5000/sip/connections/<connection_id>
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sip-registration-python/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sip-registration-python/API.md)
- [SIP Trunking Documentation](https://developers.telnyx.com/docs/sip-trunking)
- [Telnyx Portal](https://portal.telnyx.com)
