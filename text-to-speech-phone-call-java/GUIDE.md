# Text To Speech with Java and Spring

Build a production-ready Spring Boot application that initiates outbound calls and plays text-to-speech (TTS) messages using the Telnyx Voice API.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Java Server        │  receives request
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

- Java 11 or higher.
- Maven 3.6 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application configured in the Telnyx Portal with a webhook URL.
- A publicly accessible URL for receiving webhooks (use ngrok for local development).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/text-to-speech-phone-call-java
cp .env.example .env
mvn clean install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |

## Step 2: Understand the Code

The main application logic lives in `*.java`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/voice` | API endpoint |
| `POST` | `/call` | API endpoint |
| `POST` | `/speak/{callControlId}` | API endpoint |
| `GET` | `/webhooks` | Webhook handler |
| `POST` | `/voice` | API endpoint |

## Step 3: Run It

```bash
mvn spring-boot:run
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl http://localhost:5000/api/voice
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/text-to-speech-phone-call-java/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/text-to-speech-phone-call-java/API.md)
- [Messaging Documentation](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
