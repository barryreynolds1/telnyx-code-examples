# List AI Assistants with C# and ASP.NET

Build a production-ready ASP.NET Core API endpoint that retrieves and lists AI assistants using the Telnyx REST API.

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
  │  Telnyx AI Assistants│  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **AI Assistants** — [Documentation](https://developers.telnyx.com/docs/ai)

## Prerequisites

- .NET 6.0 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Visual Studio, VS Code, or any C# IDE.
- Basic familiarity with ASP.NET Core and REST APIs.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/list-ai-assistants-csharp
cp .env.example .env
dotnet restore
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |

## Step 2: Understand the Code

The main application logic lives in `*.cs`.

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

See the README for testing instructions.

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/list-ai-assistants-csharp/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/list-ai-assistants-csharp/API.md)
- [AI Assistants Documentation](https://developers.telnyx.com/docs/ai)
- [Telnyx Portal](https://portal.telnyx.com)
