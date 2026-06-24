# Hold Music with Python and Flask

Build a Flask application that plays hold music during phone calls using the Telnyx Voice API.

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
  │  Telnyx Voice API │  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **Voice API** — [Documentation](https://developers.telnyx.com/docs/voice)

## Prerequisites

- Python 3.8 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for voice calls.
- A Call Control Application configured in the Telnyx Portal.
- pip (Python package manager).
- ngrok or similar tool for webhook testing.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/hold-music-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `FLASK_DEBUG` | your_flask_debug_here |
| `TELNYX_CONNECTION_ID` | your_connection_id_here |
| `TELNYX_PHONE_NUMBER` | +15551234567 |

## Step 2: Understand the Code

The main application logic lives in `app.py`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/calls/initiate` | API endpoint |
| `POST` | `/calls/<call_control_id>/hold` | API endpoint |
| `POST` | `/calls/<call_control_id>/unhold` | API endpoint |
| `GET` | `/calls/<call_control_id>/status` | API endpoint |
| `POST` | `/webhooks/voice` | Webhook handler |

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
curl http://localhost:5000/calls/<call_control_id>/status
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/hold-music-python/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/hold-music-python/API.md)
- [Voice API Documentation](https://developers.telnyx.com/docs/voice)
- [Telnyx Portal](https://portal.telnyx.com)
