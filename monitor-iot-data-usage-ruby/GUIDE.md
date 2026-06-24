# Data Usage Monitoring with Ruby and Sinatra

Build a production-ready Sinatra application that monitors SIM card data usage using the Telnyx IoT API.

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
  │  Telnyx IoT SIM Management│  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **IoT SIM Management** — [Documentation](https://developers.telnyx.com/docs/iot)

## Prerequisites

- Ruby 2.7 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Active SIM cards in your Telnyx account with data usage history.
- Bundler (Ruby dependency manager).
- curl or Postman for testing HTTP endpoints.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/monitor-iot-data-usage-ruby
cp .env.example .env
bundle install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `DATA_LIMIT_THRESHOLD_MB` | your_data_limit_threshold_mb_here |

## Step 2: Understand the Code

The main application logic lives in `app.rb`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/sim-cards` | API endpoint |
| `GET` | `/sim-cards/:id/usage` | API endpoint |
| `GET` | `/dashboard/usage` | API endpoint |

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
curl http://localhost:5000/sim-cards
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/monitor-iot-data-usage-ruby/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/monitor-iot-data-usage-ruby/API.md)
- [IoT SIM Management Documentation](https://developers.telnyx.com/docs/iot)
- [Telnyx Portal](https://portal.telnyx.com)
