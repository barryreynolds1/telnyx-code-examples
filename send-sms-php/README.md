# Send a Single SMS with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel API endpoint that sends SMS messages using the Telnyx PHP SDK. This tutorial demonstrates the new client-based initialization pattern, proper error handling for telecom APIs, and secure credential management via Laravel's environment configuration.

## Who Is This For?

- **PHP developers** building sms features with Laravel.
- **Backend engineers** integrating telephony or messaging into existing applications.
- **DevOps teams** looking for containerized, production-ready telecom examples.
- **Startups and enterprises** replacing legacy telecom providers with a modern API-first platform.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that gives developers a single API for [voice](https://telnyx.com/products/voice-ai-agents), [messaging](https://telnyx.com/products/sms-api), [SIP](https://telnyx.com/products/sip-trunks), [AI](https://telnyx.com/ai-assistants), and [IoT](https://telnyx.com/products/iot-sim-card) — no Frankenstack required.

- **Integrated platform** — [Voice](https://telnyx.com/products/voice-ai-agents), [SMS](https://telnyx.com/products/sms-api), [SIP trunking](https://telnyx.com/products/sip-trunks), [AI assistants](https://telnyx.com/ai-assistants), and [IoT SIM management](https://telnyx.com/products/iot-sim-card) under one roof. No stitching together multiple vendors.
- **Global private network** — Calls and messages traverse the Telnyx-owned IP network for lower latency and higher reliability than the public internet.
- **Developer-first** — SDKs for Python, Node.js, Go, Ruby, Java, and PHP. Comprehensive webhook event model. Sandbox environment for testing.
- **Competitive pricing** — Pay-as-you-go with no minimums, contracts, or per-seat fees.

## Prerequisites

- PHP 8.1 or higher
- Composer (PHP package manager)
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com)
- A Telnyx phone number enabled for outbound SMS
- Laravel CLI (optional, for project scaffolding)

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a controller to handle SMS sending. This implementation validates input, initializes the Telnyx client using the new pattern, and handles all exception types at the route handler level:

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Telnyx\Client;
use Telnyx\AuthenticationError;
use Telnyx\RateLimitError;
use Telnyx\APIStatusError;
use Telnyx\APIConnectionError;

class SmsController extends Controller
{
    public function send(Request $request): JsonResponse
    {
        // Validate request payload
        $validated = $request->validate([
            'to' => 'required|string',
            'message' => 'required|string|max:1600',
        ]);

        $toNumber = $validated['to'];
        $message = $validated['message'];
        $fromNumber = env('TELNYX_PHONE_NUMBER');

        if (!$fromNumber) {
            return response()->json(['error' => 'TELNYX_PHONE_NUMBER environment variable not set'], 500);
        }

        // Validate E.164 format to prevent API errors
        if (!str_starts_with($toNumber, '+')) {
            return response()->json(['error' => 'Phone number must be in E.164 format (e.g., +15551234567)'], 400);
        }

        try {
            // Initialize client using new pattern — NOT static setApiKey()
            $client = new Client(apiKey: env('TELNYX_API_KEY'));

            // Send message using client.messages->create()
            $response = $client->messages->create([
                'from' => $fromNumber,
                'to' => $toNumber,
                'text' => $message,
            ]);

            // Extract serializable data — do not return raw response object
            return response()->json([
                'message_id' => $response->id,
                'status' => $response->to[0]->status ?? 'unknown',
                'from' => $fromNumber,
                'to' => $toNumber,
            ]);

        } catch (AuthenticationError $e) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (RateLimitError $e) {
            return response()->json(['error' => 'Rate limit exceeded. Please slow down.'], 429);
        } catch (APIStatusError $e) {
            return response()->json(['error' => $e->getMessage(), 'status_code' => $e->getCode()], $e->getCode());
        } catch (APIConnectionError $e) {
            return response()->json(['error' => 'Network error connecting to Telnyx'], 503);
        }
    }
}
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

### Issue 1: Authentication Error (401)

**Problem:** The endpoint returns `{"error": "Invalid API key"}` with HTTP 401.

**Solution:** Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Run `php artisan config:clear` to clear cached configuration, then restart the server.

### Issue 2: Invalid Phone Number Format

**Problem:** You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination.

**Solution:** Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers.

### Issue 3: Class "Telnyx\Client" Not Found

**Problem:** The application throws `Class "Telnyx\Client" not found` when hitting the endpoint.

**Solution:** Run `composer require telnyx/telnyx-php` to ensure the SDK is installed. Run `composer dump-autoload` to regenerate the autoloader. Verify the `use Telnyx\Client;` statement is present at the top of your controller file.

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SMS example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What PHP version do I need?**

PHP 8.1 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Messaging Overview](https://developers.telnyx.com/docs/messaging)
- [Send an SMS — Quickstart](https://developers.telnyx.com/docs/messaging/messages/send-message)
- [Messaging API Reference](https://developers.telnyx.com/api-reference/messages/send-a-message)
- [PHP SDK](https://developers.telnyx.com/development/sdk/php)
- [Telnyx SMS API](https://telnyx.com/products/sms-api)
- [Messaging Pricing](https://telnyx.com/pricing/messaging)

## Related Examples

- [Send Bulk SMS with PHP](/tutorials/sms/php/send-bulk-sms)
- [Receive SMS Webhooks with PHP](/tutorials/sms/php/receive-sms-webhook)
- [Implement Two-Factor Authentication with SMS](/tutorials/sms/php/otp-2fa)
