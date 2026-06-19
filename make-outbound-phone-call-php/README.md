# Outbound Call with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel endpoint that initiates outbound calls using the Telnyx PHP SDK. This tutorial demonstrates the new client-based initialization pattern, proper error handling for telecom APIs, secure credential management via environment variables, and Laravel's idiomatic patterns for routing and responses.

## Who Is This For?

- **PHP developers** building voice features with Laravel.
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

- PHP 8.1 or higher.
- Laravel 10 or higher.
- Composer (PHP package manager).
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application configured in the Telnyx Portal with a connection ID.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to encapsulate call logic. Generate it using Artisan:

```bash
php artisan make:service CallService
```

Edit `app/Services/CallService.php`:

```php
<?php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class CallService
{
    private Client $client;
    private string $fromNumber;
    private string $connectionId;

    public function __construct()
    {
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
        $this->fromNumber = getenv('TELNYX_PHONE_NUMBER');
        $this->connectionId = getenv('TELNYX_CONNECTION_ID');
    }

    /**
     * Initiate an outbound call and return serializable response data.
     *
     * @param string $toNumber Destination phone number in E.164 format.
     * @return array JSON-serializable call data.
     * @throws \InvalidArgumentException If phone number format is invalid.
     */
    public function initiateCall(string $toNumber): array
    {
        // Validate E.164 format to prevent API errors
        if (!str_starts_with($toNumber, '+')) {
            throw new \InvalidArgumentException(
                'Phone number must be in E.164 format (e.g., +15551234567)'
            );
        }

        if (!$this->fromNumber) {
            throw new \RuntimeException('TELNYX_PHONE_NUMBER environment variable not set');
        }

        if (!$this->connectionId) {
            throw new \RuntimeException('TELNYX_CONNECTION_ID environment variable not set');
        }

        // Initiate the call using the SDK
        // connection_id is REQUIRED and links to your Call Control Application
        // call_control_id is RETURNED in the response — use it for subsequent actions
        $response = $this->client->calls->dial(
            from_: $this->fromNumber,
            to: $toNumber,
            connection_id: $this->connectionId,
        );

        // Extract serializable data — SDK objects are NOT JSON-serializable
        return [
            'call_control_id' => $response->data->call_control_id,
            'from' => $this->fromNumber,
            'to' => $toNumber,
            'state' => $response->data->state ?? 'initiated',
        ];
    }
}
```

Create a controller to handle HTTP requests. Generate it using Artisan:

```bash
php artisan make:controller CallController
```

Edit `app/Http/Controllers/CallController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Services\CallService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;
use Telnyx\Exception\AuthenticationException;
use Telnyx\Exception\RateLimitException;

class CallController extends Controller
{
    private CallService $callService;

    public function __construct(CallService $callService)
    {
        $this->callService = $callService;
    }

    /**
     * Initiate an outbound call.
     *
     * POST /api/calls/initiate
     * Body: {"to": "+15559876543"}
     */
    public function initiate(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'to' => 'required|string',
        ]);

        try {
            $result = $this->callService->initiateCall($validated['to']);
            return response()->json($result, 200);

        } catch (AuthenticationException $e) {
            return response()->json(['error' => 'Invalid API key'], 401);

        } catch (RateLimitException $e) {
            return response()->json(['error' => 'Rate limit exceeded. Please slow down.'], 429);

        } catch (ApiException $e) {
            // Catch other API errors (4xx/5xx responses)
            $statusCode = $e->getHttpStatus() ?? 500;
            return response()->json(
                ['error' => $e->getMessage(), 'status_code' => $statusCode],
                $statusCode
            );

        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);

        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}
```

Register the route in `routes/api.php`:

```php
<?php

use App\Http\Controllers\CallController;
use Illuminate\Support\Facades\Route;

Route::post('/calls/initiate', [CallController::class, 'initiate']);
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your environment file and restart the Laravel server with `php artisan serve`. |
| Invalid Phone Number Format | You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination. | Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers. |
| Connection ID Not Set | The application raises `RuntimeException: TELNYX_CONNECTION_ID environment variable not set` on the first call request. | Confirm your `.env` file exists in the project root and contains the `TELNYX_CONNECTION_ID` variable. The value should be your Call Control Application ID from the Telnyx Portal. Ensure the file is named exactly `.env` (not `.env.example`). Restart the Laravel server after updating the file. |
| Call Not Initiated (500 Error) | The endpoint returns a 500 error with a message about the API connection or response parsing. | Verify that your `TELNYX_PHONE_NUMBER` is a valid Telnyx phone number in E.164 format and is enabled for outbound calls in the Telnyx Portal. Check that the `TELNYX_CONNECTION_ID` corresponds to an active Call Control Application. Review the Laravel logs in `storage/logs/laravel.log` for detailed error messages. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this Voice example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What PHP version do I need?**

PHP 8.1 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Voice API Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [AI Assistant Start](https://developers.telnyx.com/docs/voice/programmable-voice/ai-assistant-start)
- [Call Control API Reference](https://developers.telnyx.com/api-reference/call-commands/dial)
- [PHP SDK](https://developers.telnyx.com/development/sdk/php)
- [Telnyx Voice API](https://telnyx.com/products/voice-api)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [Receive Inbound Call Webhooks with PHP](/tutorials/voice/php/inbound-call-webhook).
- [Record Calls with PHP](/tutorials/voice/php/call-recording).
- [Transfer Calls with PHP](/tutorials/voice/php/call-transfer).
