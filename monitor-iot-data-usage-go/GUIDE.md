# Data Usage Monitoring with Go and Gin

Build a production-ready Gin web service that monitors SIM card data usage in real time using the Telnyx IoT API.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Go Server          │  receives request
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

- Go 1.19 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Active SIM cards in your Telnyx account with data plans.
- `go get` (Go package manager).
- curl or Postman for testing HTTP endpoints.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/monitor-iot-data-usage-go
cp .env.example .env
go mod tidy
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `MONITOR_PORT` | your_monitor_port_here |

## Step 2: Understand the Code

The main application logic lives in `main.go`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/sim-cards/usage` | API endpoint |
| `GET` | `/sim-cards/:id/usage` | API endpoint |

## Step 3: Run It

```bash
go run main.go
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl http://localhost:5000/sim-cards/usage
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/monitor-iot-data-usage-go/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/monitor-iot-data-usage-go/API.md)
- [IoT SIM Management Documentation](https://developers.telnyx.com/docs/iot)
- [Telnyx Portal](https://portal.telnyx.com)
