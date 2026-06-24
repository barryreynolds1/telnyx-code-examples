# OTP 2FA with Go and Gin

Build a production-ready two-factor authentication (2FA) system using Go, Gin, and the Telnyx SMS API.

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
  │  Telnyx Messaging │  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **Messaging** — [Documentation](https://developers.telnyx.com/docs/messaging)

## Prerequisites

- Go 1.19 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound SMS.
- Basic familiarity with Go and REST APIs.
- `go get` (Go package manager).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sms-two-factor-auth-go
cp .env.example .env
go mod tidy
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `OTP_EXPIRY_MINUTES` | your_otp_expiry_minutes_here |
| `TELNYX_PHONE_NUMBER` | +15551234567 |

## Step 2: Understand the Code

The main application logic lives in `main.go`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/otp/request` | API endpoint |
| `POST` | `/otp/verify` | API endpoint |

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
curl -X POST http://localhost:5000/otp/request \
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

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-go/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-go/API.md)
- [Messaging Documentation](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
