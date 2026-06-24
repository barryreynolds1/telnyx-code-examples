# Ivr Menu with PHP and Laravel

Build a production-ready Interactive Voice Response (IVR) system using Laravel and the Telnyx Voice API.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  PHP Server         │  receives request
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

- PHP 8.1 or higher.
- Laravel 10 or higher.
- Composer (PHP package manager).
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound calls.
- A publicly accessible URL for webhook callbacks (ngrok or similar for local development).
- Basic understanding of Laravel routing and middleware.

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-ivr-phone-menu-php
cp .env.example .env
composer install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |

## Step 2: Understand the Code

The main application logic lives in `index.php`.

## Step 3: Run It

```bash
php -S localhost:5000 index.php
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

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/build-ivr-phone-menu-php/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/build-ivr-phone-menu-php/API.md)
- [Voice API Documentation](https://developers.telnyx.com/docs/voice)
- [Telnyx Portal](https://portal.telnyx.com)
