<?php
// app/Services/SimCardService.php

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

// app/Http/Controllers/SimCardController.php

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

// routes/api.php

use App\Http\Controllers\SimCardController;
use Illuminate\Support\Facades\Route;

Route::post('/sim-cards/activate', [SimCardController::class, 'activate']);
Route::get('/sim-cards/{simCardId}', [SimCardController::class, 'show']);
