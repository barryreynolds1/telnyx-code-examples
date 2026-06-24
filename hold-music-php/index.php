<?php

// app/Services/TelnyxCallService.php
namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class TelnyxCallService
{
    private Client $client;
    private string $phoneNumber;
    private string $connectionId;
    private string $holdMusicUrl;

    public function __construct()
    {
        $this->client = new Client(apiKey: config('services.telnyx.api_key'));
        $this->phoneNumber = config('services.telnyx.phone_number');
        $this->connectionId = config('services.telnyx.connection_id');
        $this->holdMusicUrl = config('services.telnyx.hold_music_url');
    }

    public function initiateCall(string $toNumber): array
    {
        if (!str_starts_with($toNumber, '+')) {
            throw new \InvalidArgumentException('Phone number must be in E.164 format (e.g., +15551234567)');
        }

        try {
            $response = $this->client->calls->dial(
                from_: $this->phoneNumber,
                to: $toNumber,
                connection_id: $this->connectionId,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'to' => $toNumber,
                'from' => $this->phoneNumber,
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to initiate call: ' . $e->getMessage());
        }
    }

    public function answerCall(string $callControlId): array
    {
        try {
            $response = $this->client->calls->actions->answer(
                call_control_id: $callControlId,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'state' => $response->data->state ?? 'answered',
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to answer call: ' . $e->getMessage());
        }
    }

    public function startHoldMusic(string $callControlId): array
    {
        try {
            $response = $this->client->calls->actions->playback_start(
                call_control_id: $callControlId,
                audio_url: $this->holdMusicUrl,
                loop: true,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'playback_started' => true,
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to start hold music: ' . $e->getMessage());
        }
    }

    public function stopHoldMusic(string $callControlId): array
    {
        try {
            $response = $this->client->calls->actions->playback_stop(
                call_control_id: $callControlId,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'playback_stopped' => true,
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to stop hold music: ' . $e->getMessage());
        }
    }

    public function hangupCall(string $callControlId): array
    {
        try {
            $response = $this->client->calls->actions->hangup(
                call_control_id: $callControlId,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'hangup_initiated' => true,
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to hangup call: ' . $e->getMessage());
        }
    }

    public function getCallStatus(string $callControlId): array
    {
        try {
            $response = $this->client->calls->retrieve_status(
                call_control_id: $callControlId,
            );

            return [
                'call_control_id' => $response->data->call_control_id,
                'state' => $response->data->state,
                'is_alive' => $response->data->is_alive,
            ];
        } catch (ApiException $e) {
            throw new \RuntimeException('Failed to retrieve call status: ' . $e->getMessage());
        }
    }
}

// app/Http/Controllers/CallController.php
namespace App\Http\Controllers;

use App\Services\TelnyxCallService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CallController extends Controller
{
    private TelnyxCallService $callService;

    public function __construct(TelnyxCallService $callService)
    {
        $this->callService = $callService;
    }

    public function initiateCall(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'to' => 'required|string|regex:/^\+\d{1,15}$/',
        ]);

        try {
            $result = $this->callService->initiateCall($validated['to']);
            return response()->json($result, 200);
        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function webhook(Request $request): JsonResponse
    {
        $payload = $request->all();

        $eventType = $payload['data']['event_type'] ?? null;
        $callControlId = $payload['data']['payload']['call_control_id'] ?? null;

        if (!$eventType || !$callControlId) {
            return response()->json(['status' => 'ignored'], 200);
        }

        try {
            switch ($eventType) {
                case 'call.initiated':
                    \Log::info('Call initiated', ['call_control_id' => $callControlId]);
                    break;

                case 'call.answered':
                    \Log::info('Call answered, starting hold music', ['call_control_id' => $callControlId]);
                    $this->callService->startHoldMusic($callControlId);
                    break;

                case 'call.hangup':
                    \Log::info('Call hangup', ['call_control_id' => $callControlId]);
                    break;

                default:
                    \Log::debug('Unhandled event type', ['event_type' => $eventType]);
            }

            return response()->json(['status' => 'processed'], 200);
        } catch (\RuntimeException $e) {
            \Log::error('Webhook processing error', ['error' => $e->getMessage()]);
            return response()->json(['status' => 'error', 'message' => $e->getMessage()], 200);
        }
    }

    public function getStatus(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'call_control_id' => 'required|string',
        ]);

        try {
            $result = $this->callService->getCallStatus($validated['call_control_id']);
            return response()->json($result, 200);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function hangupCall(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'call_control_id' => 'required|string',
        ]);

        try {
            $this->callService->stopHoldMusic($validated['call_control_id']);
            $result = $this->callService->hangupCall($validated['call_control_id']);
            return response()->json($result, 200);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}

// routes/api.php
use App\Http\Controllers\CallController;
use Illuminate\Support\Facades\Route;

Route::post('/calls/initiate', [CallController::class, 'initiateCall']);
Route::post('/calls/status', [CallController::class, 'getStatus']);
Route::post('/calls/hangup', [CallController::class, 'hangupCall']);
Route::post('/webhooks/call', [CallController::class, 'webhook']);

// config/services.php (add to existing array)
'telnyx' => [
    'api_key' => env('TELNYX_API_KEY'),
    'phone_number' => env('TELNYX_PHONE_NUMBER'),
    'connection_id' => env('TELNYX_CONNECTION_ID'),
    'hold_music_url' => env('HOLD_MUSIC_URL'),
    'webhook_url' => env('WEBHOOK_URL'),
],
