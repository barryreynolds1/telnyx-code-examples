# Conference Call with Ruby and Sinatra

Build a production-ready Sinatra application that manages multi-participant conference calls using the Telnyx Voice API.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Ruby Server        │  receives request
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

- Ruby 2.7 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application configured in the Telnyx Portal (to obtain your `TELNYX_CONNECTION_ID`).
- Bundler (Ruby dependency manager).
- A publicly accessible URL for webhook callbacks (ngrok recommended for local development).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-conference-calling-ruby
cp .env.example .env
bundle install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `TELNYX_CONNECTION_ID` | your_connection_id_here |
| `TELNYX_PHONE_NUMBER` | +15551234567 |

## Step 2: Understand the Code

The main application logic lives in `app.rb`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/conferences/create` | API endpoint |
| `POST` | `/conferences/:conference_id/invite` | API endpoint |
| `GET` | `/conferences/:conference_id/status` | API endpoint |
| `POST` | `/conferences/:conference_id/hangup` | API endpoint |
| `POST` | `/webhooks/call-events` | Webhook handler |
| `GET` | `/` | API endpoint |

## Step 3: Run It

```bash
ruby app.rb
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl http://localhost:5000/conferences/:conference_id/status
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/build-conference-calling-ruby/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/build-conference-calling-ruby/API.md)
- [Voice API Documentation](https://developers.telnyx.com/docs/voice)
- [Telnyx Portal](https://portal.telnyx.com)
