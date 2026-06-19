<?php
/**
 * Production-ready Laravel application for initiating outbound calls via Telnyx.
 *
 * File structure:
 * - app/Services/CallService.php
 * - app/Http/Controllers/CallController.php
 * - routes/api.php
 * - .env (with TELNYX_API_KEY, TELNYX_PHONE_NUMBER, TELNYX_CONNECTION_ID)
 */

// ============================================================================
// app/Services/CallService.php
// ============================================================================

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

// ============================================================================
// app/Http/Controllers/CallController.php
// ============================================================================

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

// ============================================================================
// routes/api.php
// ============================================================================

use App\Http\Controllers\CallController;
use Illuminate\Support\Facades\Route;

Route::post('/calls/initiate', [CallController::class, 'initiate']);

// ============================================================================
// .env
// ============================================================================

TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE
