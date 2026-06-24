# Inbound Call Webhook with C# and ASP.NET

Build a production-ready ASP.NET endpoint that receives and processes inbound call webhooks from Telnyx.

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
  │  Telnyx Voice API │  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **Voice API** — [Documentation](https://developers.telnyx.com/docs/voice)

## Prerequisites

- .NET 6.0 or higher installed on your system.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound calls.
- A publicly accessible URL (ngrok, Cloudflare Tunnel, or deployed server) to receive webhooks.
- Basic familiarity with C# and ASP.NET Core.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/route-phone-calls-to-ai-agent-csharp
cp .env.example .env
dotnet restore
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |

## Step 2: Understand the Code

The main application logic lives in `*.cs`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `webhook` | Webhook handler |
| `GET` | `status` | API endpoint |

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
curl http://localhost:5000status
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/route-phone-calls-to-ai-agent-csharp/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/route-phone-calls-to-ai-agent-csharp/API.md)
- [Voice API Documentation](https://developers.telnyx.com/docs/voice)
- [Telnyx Portal](https://portal.telnyx.com)
