# OTP 2FA with C# and ASP.NET

Build a production-ready ASP.NET application that implements two-factor authentication (2FA) using one-time passwords (OTPs) delivered via SMS through the Telnyx API.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  C# Server          │  receives request
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

- .NET 6.0 or higher installed.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound SMS.
- Visual Studio, Visual Studio Code, or the .NET CLI.
- Basic familiarity with ASP.NET Core and HTTP APIs.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sms-two-factor-auth-csharp
cp .env.example .env
dotnet restore
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `OTP_EXPIRY_SECONDS` | your_otp_expiry_seconds_here |
| `OTP_LENGTH` | your_otp_length_here |
| `TELNYX_PHONE_NUMBER` | +15551234567 |

## Step 2: Understand the Code

The main application logic lives in `*.cs`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `request-otp` | API endpoint |
| `POST` | `verify-otp` | API endpoint |

## Step 3: Run It

```bash
dotnet run
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl -X POST http://localhost:5000request-otp \
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

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-csharp/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-csharp/API.md)
- [Messaging Documentation](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
