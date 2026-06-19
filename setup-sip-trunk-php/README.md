# SIP Trunking Setup with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel application that manages SIP trunk connections using the Telnyx PHP SDK. This tutorial demonstrates how to create SIP connections, configure authentication, and route inbound calls to your PBX or SBC. You'll learn the new client-based initialization pattern, proper error handling for telecom APIs, and secure credential management via environment variables.

## Who Is This For?

- **PHP developers** building sip features with Laravel.
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
- A Telnyx phone number enabled for voice calls.
- A publicly accessible SIP endpoint (PBX, SBC, or softphone) for receiving inbound calls.
- Basic understanding of SIP concepts and Laravel routing.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to encapsulate SIP connection logic. Generate a new service:

```bash
php artisan make:service SipTrunkingService
```

Edit `app/Services/SipTrunkingService.php`:

```php
<?php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class SipTrunkingService
{
    private Client $client;

    public function __construct()
    {
        // Initialize client with the new SDK pattern
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    /**
     * Create a new SIP connection with credential authentication.
     *
     * @param string $name Connection name for identification.
     * @param string $username SIP registration username.
     * @param string $password SIP registration password.
     * @param string $sipAddress Target SIP endpoint (e.g., sip.yourdomain.com:5060).
     * @return array JSON-serializable connection data.
     */
    public function createSipConnection(
        string $name,
        string $username,
        string $password,
        string $sipAddress
    ): array {
        $response = $this->client->sip_connections->create([
            'connection_name' => $name,
            'active' => true,
            'credentials' => [
                'sip_username' => $username,
                'sip_password' => $password,
            ],
            'inbound' => [
                'sip_subdomain' => 'telnyx',
            ],
            'outbound' => [
                'outbound_voice_profile_id' => null, // Set after creating profile
            ],
        ]);

        // Extract serializable data — SDK objects are NOT JSON-serializable
        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
            'created_at' => $response->data->created_at,
        ];
    }

    /**
     * List all SIP connections.
     *
     * @return array Array of connection data.
     */
    public function listSipConnections(): array
    {
        $response = $this->client->sip_connections->list();

        // Map SDK objects to plain arrays for JSON serialization
        return array_map(function ($connection) {
            return [
                'id' => $connection->id,
                'name' => $connection->connection_name,
                'username' => $connection->credentials->sip_username ?? null,
                'active' => $connection->active,
                'created_at' => $connection->created_at,
            ];
        }, $response->data);
    }

    /**
     * Retrieve a specific SIP connection by ID.
     *
     * @param string $connectionId The SIP connection ID.
     * @return array Connection data.
     */
    public function getSipConnection(string $connectionId): array
    {
        $response = $this->client->sip_connections->retrieve($connectionId);

        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
            'created_at' => $response->data->created_at,
            'inbound' => $response->data->inbound,
            'outbound' => $response->data->outbound,
        ];
    }

    /**
     * Update an existing SIP connection.
     *
     * @param string $connectionId The SIP connection ID.
     * @param array $updates Fields to update.
     * @return array Updated connection data.
     */
    public function updateSipConnection(string $connectionId, array $updates): array
    {
        $response = $this->client->sip_connections->update($connectionId, $updates);

        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
        ];
    }

    /**
     * Delete a SIP connection.
     *
     * @param string $connectionId The SIP connection ID.
     * @return bool True if deletion was successful.
     */
    public function deleteSipConnection(string $connectionId): bool
    {
        $this->client->sip_connections->delete($connectionId);
        return true;
    }
}
```

Create a controller to handle HTTP requests. Generate a new controller:

```bash
php artisan make:controller SipConnectionController
```

Edit `app/Http/Controllers/SipConnectionController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Services\SipTrunkingService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;
use Telnyx\Exception\AuthenticationException;
use Telnyx\Exception\RateLimitException;

class SipConnectionController extends Controller
{
    private SipTrunkingService $sipService;

    public function __construct(SipTrunkingService $sipService)
    {
        $this->sipService = $sipService;
    }

    /**
     * Create a new SIP connection.
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'username' => 'required|string|max:255',
            'password' => 'required|string|min:8',
            'sip_address' => 'required|string',
        ]);

        try {
            $connection = $this->sipService->createSipConnection(
                $validated['name'],
                $validated['username'],
                $validated['password'],
                $validated['sip_address']
            );

            return response()->json($connection, 201);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (RateLimitException) {
            return response()->json(['error' => 'Rate limit exceeded'], 429);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage(), 'status_code' => $e->getHttpStatus()],
                $e->getHttpStatus()
            );
        }
    }

    /**
     * List all SIP connections.
     */
    public function index(): JsonResponse
    {
        try {
            $connections = $this->sipService->listSipConnections();
            return response()->json($connections);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    /**
     * Retrieve a specific SIP connection.
     */
    public function show(string $id): JsonResponse
    {
        try {
            $connection = $this->sipService->getSipConnection($id);
            return response()->json($connection);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    /**
     * Update a SIP connection.
     */
    public function update(Request $request, string $id): JsonResponse
    {
        $validated = $request->validate([
            'active' => 'sometimes|boolean',
            'password' => 'sometimes|string|min:8',
        ]);

        try {
            $connection = $this->sipService->updateSipConnection($id, $validated);
            return response()->json($connection);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    /**
     * Delete a SIP connection.
     */
    public function destroy(string $id): JsonResponse
    {
        try {
            $this->sipService->deleteSipConnection($id);
            return response()->json(['message' => 'Connection deleted successfully']);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }
}
```

Register the routes in `routes/api.php`:

```php
<?php

use App\Http\Controllers\SipConnectionController;
use Illuminate\Support\Facades\Route;

Route::apiResource('sip-connections', SipConnectionController::class);
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the Laravel development server after updating `.env` to reload environment variables. |
| SIP Connection Creation Fails | The API returns a 400 error with message about invalid credentials or connection name. | Ensure the `connection_name` is unique and contains only alphanumeric characters and hyphens. Verify the `sip_username` and `sip_password` meet Telnyx requirements (username 3-32 chars, password 8+ chars). Check that your SIP endpoint address is in the correct format (e.g., `sip.yourdomain.com:5060`). |
| Rate Limit Exceeded (429) | The endpoint returns `{"error": "Rate limit exceeded"}` with HTTP 429. | Telnyx API has rate limits. Implement exponential backoff retry logic in your application. Space out API calls and cache SIP connection data when possible. Contact Telnyx support if you need higher rate limits for your use case. |
| Service Not Binding | Laravel throws "Target class [SipTrunkingService] does not exist" error. | Ensure the service class file is located at `app/Services/SipTrunkingService.php` with the correct namespace `App\Services`. Run `composer dump-autoload` to refresh Laravel's autoloader. Verify the controller imports the service with `use App\Services\SipTrunkingService;`. |
| Environment Variables Not Loading | The application throws "TELNYX_API_KEY is not set" or similar error. | Confirm your `.env` file exists in the project root directory (same level as `artisan`). Verify the file is named exactly `.env` (not `.env.example` or `.env.local`). Run `php artisan config:clear` to clear cached configuration. Restart the development server with `php artisan serve`. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SIP example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What PHP version do I need?**

PHP 8.1 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [SIP Trunking Get Started](https://developers.telnyx.com/docs/voice/sip-trunking/get-started)
- [SIP Configuration Guides](https://developers.telnyx.com/docs/voice/sip-trunking/configuration-guides)
- [PHP SDK](https://developers.telnyx.com/development/sdk/php)
- [Telnyx SIP Trunks](https://telnyx.com/products/sip-trunks)
- [SIP Trunking Pricing](https://telnyx.com/pricing/elastic-sip)

## Related Examples

- [Configure SIP Authentication Methods](/tutorials/sip/php/sip-authentication).
- [Set Up Failover Routing for High Availability](/tutorials/sip/php/failover-routing).
- [Handle Inbound SIP Calls with Webhooks](/tutorials/sip/php/inbound-sip-routing).
