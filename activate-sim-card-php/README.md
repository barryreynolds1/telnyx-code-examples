# SIM Activation with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel application that activates SIM cards using the Telnyx IoT API. This tutorial demonstrates the new PHP SDK client initialization pattern, proper error handling for IoT operations, and secure credential management via environment variables. You'll create a REST endpoint that activates a SIM card and returns its updated status.

## Who Is This For?

- **PHP developers** building iot features with Laravel.
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
- Composer (PHP package manager).
- Laravel 10 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- At least one SIM card in your Telnyx account (in `ready` or `inactive` status).
- The SIM card ID (available in the Telnyx Portal under IoT → SIM Cards).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle SIM card activation logic. Generate a new service:

```bash
php artisan make:controller SimCardController
```

Create a service class to encapsulate the Telnyx API interaction:

```bash
mkdir -p app/Services
```

Create `app/Services/SimCardService.php`:

```php
<?php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class SimCardService
{
    private Client $client;

    public function __construct()
    {
        // Initialize client with the new SDK pattern
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    /**
     * Activate a SIM card and return JSON-serializable response data.
     *
     * @param string $simCardId The SIM card ID to activate.
     * @return array Activation response with SIM card details.
     * @throws ApiException If the API call fails.
     */
    public function activateSimCard(string $simCardId): array
    {
        // Validate SIM card ID format (basic check)
        if (empty($simCardId)) {
            throw new \InvalidArgumentException('SIM card ID cannot be empty');
        }

        // Call the Telnyx API to activate the SIM card
        $response = $this->client->simCards->activate($simCardId);

        // Extract serializable data — SDK objects are NOT JSON-serializable
        return [
            'id' => $response->data->id,
            'iccid' => $response->data->iccid,
            'status' => $response->data->status,
            'sim_card_group_id' => $response->data->sim_card_group_id ?? null,
            'activated_at' => $response->data->activated_at ?? null,
        ];
    }

    /**
     * Retrieve SIM card details without activation.
     *
     * @param string $simCardId The SIM card ID to retrieve.
     * @return array SIM card details.
     * @throws ApiException If the API call fails.
     */
    public function getSimCard(string $simCardId): array
    {
        if (empty($simCardId)) {
            throw new \InvalidArgumentException('SIM card ID cannot be empty');
        }

        $response = $this->client->simCards->retrieve($simCardId);

        return [
            'id' => $response->data->id,
            'iccid' => $response->data->iccid,
            'status' => $response->data->status,
            'sim_card_group_id' => $response->data->sim_card_group_id ?? null,
            'activated_at' => $response->data->activated_at ?? null,
        ];
    }
}
```

Update `app/Http/Controllers/SimCardController.php` to handle HTTP requests:

```php
<?php

namespace App\Http\Controllers;

use App\Services\SimCardService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;

class SimCardController extends Controller
{
    private SimCardService $simCardService;

    public function __construct(SimCardService $simCardService)
    {
        $this->simCardService = $simCardService;
    }

    /**
     * Activate a SIM card via HTTP POST.
     *
     * @param Request $request HTTP request containing sim_card_id.
     * @return JsonResponse Activation result or error.
     */
    public function activate(Request $request): JsonResponse
    {
        // Validate request payload
        $validated = $request->validate([
            'sim_card_id' => 'required|string',
        ]);

        try {
            $result = $this->simCardService->activateSimCard($validated['sim_card_id']);
            return response()->json($result, 200);

        } catch (\Telnyx\Exception\AuthenticationException $e) {
            return response()->json(['error' => 'Invalid API key'], 401);

        } catch (\Telnyx\Exception\RateLimitException $e) {
            return response()->json(['error' => 'Rate limit exceeded. Please slow down.'], 429);

        } catch (\Telnyx\Exception\ApiException $e) {
            // Handle other API errors (4xx/5xx)
            $statusCode = $e->getHttpStatus() ?? 500;
            return response()->json([
                'error' => $e->getMessage(),
                'status_code' => $statusCode,
            ], $statusCode);

        } catch (\Telnyx\Exception\ApiConnectionException $e) {
            return response()->json(['error' => 'Network error connecting to Telnyx'], 503);

        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);
        }
    }

    /**
     * Retrieve SIM card status via HTTP GET.
     *
     * @param string $simCardId The SIM card ID.
     * @return JsonResponse SIM card details or error.
     */
    public function show(string $simCardId): JsonResponse
    {
        try {
            $result = $this->simCardService->getSimCard($simCardId);
            return response()->json($result, 200);

        } catch (\Telnyx\Exception\AuthenticationException $e) {
            return response()->json(['error' => 'Invalid API key'], 401);

        } catch (\Telnyx\Exception\ApiException $e) {
            $statusCode = $e->getHttpStatus() ?? 500;
            return response()->json([
                'error' => $e->getMessage(),
                'status_code' => $statusCode,
            ], $statusCode);

        } catch (\Telnyx\Exception\ApiConnectionException $e) {
            return response()->json(['error' => 'Network error connecting to Telnyx'], 503);

        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);
        }
    }
}
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your `.env` file and restart the Laravel development server with `php artisan serve`. |
| SIM Card Not Found (404) | The API returns a 404 error stating the SIM card ID does not exist. | Confirm the SIM card ID is correct by checking the [Telnyx Portal](https://portal.telnyx.com) under IoT → SIM Cards. SIM card IDs typically start with `sim_`. Verify the SIM card exists in your account and is not deleted. |
| Invalid SIM Card Status | The activation request fails with an error about the SIM card status being incompatible (e.g., already active or suspended). | Check the current status of the SIM card in the Telnyx Portal. SIM cards can only be activated from `ready` or `inactive` status. If the SIM is already `active`, the activation call will fail. If it is `suspended`, you may need to unsuspend it first via the Portal or API. |
| Environment Variable Not Loaded | The application raises an error about missing `TELNYX_API_KEY` or `getenv()` returns null. | Confirm your `.env` file exists in the project root (same directory as `composer.json`). Ensure the file contains `TELNYX_API_KEY=YOUR_API_KEY_HERE` with no spaces around the `=`. Restart the Laravel development server with `php artisan serve` to reload environment variables. |
| Network Error (503) | The endpoint returns `{"error": "Network error connecting to Telnyx"}` with HTTP 503. | Verify your internet connection is active and can reach external APIs. Check if the Telnyx API service is operational by visiting the [Telnyx Status Page](https://status.telnyx.com). If the issue persists, try again after a few moments as it may be a temporary connectivity issue. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this IoT example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What PHP version do I need?**

PHP 8.1 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [IoT SIM Get Started](https://developers.telnyx.com/docs/iot-sim/get-started)
- [SIM Card API Reference](https://developers.telnyx.com/api-reference/sim-cards/get-all-sim-cards)
- [PHP SDK](https://developers.telnyx.com/development/sdk/php)
- [Telnyx IoT SIM Cards](https://telnyx.com/products/iot-sim-card)
- [IoT Data Plans Pricing](https://telnyx.com/pricing/iot-data-plans)

## Related Examples

- [Monitor SIM Card Data Usage](/tutorials/iot/php/data-usage-monitoring).
- [Configure Custom APN Settings](/tutorials/iot/php/apn-configuration).
- [Handle SIM Status Change Webhooks](/tutorials/iot/php/sim-status-webhook).
