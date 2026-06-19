# Receive SMS Webhook with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel webhook endpoint that receives inbound SMS messages from Telnyx. This tutorial demonstrates how to configure a Messaging Profile with a webhook URL, handle incoming SMS events, and persist message data using Laravel's built-in features. You'll learn the new SDK initialization pattern, proper error handling for telecom APIs, and secure credential management via environment variables.

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

- PHP 8.1 or higher.
- Laravel 10 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound SMS.
- Composer (PHP package manager).
- A publicly accessible URL (ngrok, Cloudflare Tunnel, or deployed server) to receive webhooks.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a controller to handle webhook requests:

```bash
php artisan make:controller WebhookController
```

Edit `app/Http/Controllers/WebhookController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Models\InboundMessage;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class WebhookController extends Controller
{
    /**
     * Handle inbound SMS webhook from Telnyx.
     * 
     * Telnyx sends a POST request with message.received event.
     * Extract message data and persist to database.
     */
    public function handleSmsWebhook(Request $request): JsonResponse
    {
        // Validate the request contains required webhook data
        $payload = $request->all();

        if (empty($payload['data'])) {
            return response()->json(['error' => 'Invalid webhook payload'], 400);
        }

        $data = $payload['data'];
        $attributes = $data['attributes'] ?? [];

        // Extract message details from webhook event
        $messageId = $data['id'] ?? null;
        $from = $attributes['from'][0]['phone_number'] ?? null;
        $to = $attributes['to'][0]['phone_number'] ?? null;
        $text = $attributes['text'] ?? '';
        $direction = $attributes['direction'] ?? 'inbound';

        // Validate required fields
        if (!$messageId || !$from || !$to) {
            return response()->json(['error' => 'Missing required message fields'], 400);
        }

        // Store the inbound message in the database
        try {
            InboundMessage::create([
                'message_id' => $messageId,
                'from' => $from,
                'to' => $to,
                'text' => $text,
                'direction' => $direction,
                'status' => 'received',
                'raw_payload' => $payload,
            ]);

            // Log successful receipt (optional)
            \Log::info('Inbound SMS received', [
                'message_id' => $messageId,
                'from' => $from,
                'to' => $to,
            ]);

            return response()->json(['status' => 'received'], 200);

        } catch (\Exception $e) {
            \Log::error('Failed to store inbound message', [
                'error' => $e->getMessage(),
                'message_id' => $messageId,
            ]);

            return response()->json(['error' => 'Failed to process webhook'], 500);
        }
    }

    /**
     * Retrieve all inbound messages.
     * 
     * Returns a JSON-serializable list of stored messages.
     */
    public function listMessages(): JsonResponse
    {
        try {
            $messages = InboundMessage::orderBy('created_at', 'desc')->get();

            $data = $messages->map(function ($message) {
                return [
                    'id' => $message->id,
                    'message_id' => $message->message_id,
                    'from' => $message->from,
                    'to' => $message->to,
                    'text' => $message->text,
                    'direction' => $message->direction,
                    'status' => $message->status,
                    'created_at' => $message->created_at->toIso8601String(),
                ];
            })->toArray();

            return response()->json($data, 200);

        } catch (\Exception $e) {
            \Log::error('Failed to retrieve messages', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Failed to retrieve messages'], 500);
        }
    }

    /**
     * Retrieve a single inbound message by ID.
     */
    public function getMessage($id): JsonResponse
    {
        try {
            $message = InboundMessage::findOrFail($id);

            return response()->json([
                'id' => $message->id,
                'message_id' => $message->message_id,
                'from' => $message->from,
                'to' => $message->to,
                'text' => $message->text,
                'direction' => $message->direction,
                'status' => $message->status,
                'created_at' => $message->created_at->toIso8601String(),
            ], 200);

        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json(['error' => 'Message not found'], 404);
        } catch (\Exception $e) {
            \Log::error('Failed to retrieve message', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Failed to retrieve message'], 500);
        }
    }
}
```

Register the webhook route in `routes/api.php`:

```php
<?php

use App\Http\Controllers\WebhookController;
use Illuminate\Support\Facades\Route;

// Webhook endpoint for inbound SMS (no authentication required for Telnyx)
Route::post('/webhooks/sms', [WebhookController::class, 'handleSmsWebhook'])->withoutMiddleware('api');

// API endpoints to retrieve messages (protected by Laravel's default middleware)
Route::get('/messages', [WebhookController::class, 'listMessages']);
Route::get('/messages/{id}', [WebhookController::class, 'getMessage']);
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Webhook not triggering | SMS is sent to your Telnyx number but the webhook endpoint is never called. | Verify the webhook URL in your Messaging Profile matches your public URL exactly (including the protocol and path). Ensure your server is running and publicly accessible using ngrok or a deployed server. Check your firewall and router settings to allow inbound HTTPS traffic on port 443. Test the URL directly in a browser to confirm it's reachable. |
| "Invalid webhook payload" error | The webhook endpoint returns HTTP 400 with `{"error": "Invalid webhook payload"}`. | Verify that Telnyx is sending the correct JSON structure. Check your Laravel logs (`storage/logs/laravel.log`) for detailed error messages. Ensure the `data` key exists in the incoming request. Use a tool like Postman to manually send a test webhook payload to your endpoint to debug the structure. |
| Messages not persisting to database | Webhook returns 200 but no messages appear in the database when querying `/api/messages`. | Verify the database migration ran successfully with `php artisan migrate:status`. Check that the `inbound_messages` table exists in your database using a database client. Review Laravel logs for database connection errors. Ensure the `InboundMessage` model's `$fillable` array includes all fields being inserted. Test the database connection with `php artisan tinker` and manually create a record. |
| "Missing required message fields" error | The webhook returns HTTP 400 with `{"error": "Missing required message fields"}`. | The incoming webhook payload structure may differ from expected. Log the raw payload by adding `\Log::info('Webhook payload', $payload)` before validation. Check the Telnyx webhook documentation to confirm the exact structure of `from`, `to`, and other fields. Adjust the extraction logic in `handleSmsWebhook()` to match the actual payload structure. |
| ngrok URL expires or changes | After restarting ngrok, the webhook URL in your Messaging Profile becomes invalid. | Use ngrok's paid plan to reserve a static subdomain, or update your Messaging Profile webhook URL each time ngrok restarts. Alternatively, deploy your Laravel application to a production server with a permanent domain name and update the webhook URL once. |

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

- [Send a Single SMS with PHP and Laravel](/tutorials/sms/php/send-single-sms).
- [Send Bulk SMS Messages with PHP and Laravel](/tutorials/sms/php/send-bulk-sms).
- [Implement Two-Factor Authentication with SMS and PHP](/tutorials/sms/php/otp-2fa).
