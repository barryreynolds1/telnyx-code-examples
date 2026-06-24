# OTP 2FA with PHP and Laravel

Build a production-ready Laravel application that implements two-factor authentication (2FA) using one-time passwords (OTPs) delivered via SMS.

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
  │  Telnyx Messaging │  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **Messaging** — [Documentation](https://developers.telnyx.com/docs/messaging)

## Prerequisites

- PHP 8.1 or higher.
- Laravel 10 or higher.
- Composer (PHP package manager).
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound SMS.
- A database (SQLite for development is fine).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/sms-two-factor-auth-php
cp .env.example .env
composer install
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |

## Step 2: Understand the Code

The main application logic lives in `index.php`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/auth/2fa/request-otp` | API endpoint |
| `POST` | `/auth/2fa/verify-otp` | API endpoint |
| `POST` | `/auth/2fa/resend-otp` | API endpoint |

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

```bash
curl -X POST http://localhost:5000/auth/2fa/request-otp \
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

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-php/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/sms-two-factor-auth-php/API.md)
- [Messaging Documentation](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
