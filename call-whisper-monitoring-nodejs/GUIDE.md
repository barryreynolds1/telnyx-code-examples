# Whisper Prompt with Node.js and Express

Build a production-ready Express application that initiates outbound calls with a whisper prompt—a message played to the caller before the call is connected to the recipient.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Node.js Server     │  receives request
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

- Node.js 16 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application configured in the Telnyx Portal with a connection ID.
- A publicly accessible webhook URL (use ngrok for local development).
- npm (Node.js package manager).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/call-whisper-monitoring-nodejs
cp .env.example .env
npm install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `PORT` | 5000 |
| `TELNYX_CONNECTION_ID` | your_connection_id_here |
| `TELNYX_PHONE_NUMBER` | +15551234567 |
| `WEBHOOK_URL` | https://your-domain.com/webhook |

## Step 2: Understand the Code

The main application logic lives in `server.js`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/call/initiate` | API endpoint |
| `POST` | `/webhooks/call` | Webhook handler |

## Step 3: Run It

```bash
node server.js
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl -X POST http://localhost:5000/call/initiate \
  -H "Content-Type: application/json" \
  -d '{"to": "+15551234567"}'
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/call-whisper-monitoring-nodejs/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/call-whisper-monitoring-nodejs/API.md)
- [Voice API Documentation](https://developers.telnyx.com/docs/voice)
- [Telnyx Portal](https://portal.telnyx.com)
