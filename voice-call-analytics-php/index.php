<?php
// app/Services/CallService.php
namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;
use App\Models\CallAnalytic;
use Carbon\Carbon;

class CallService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    public function initiateCall(string $toNumber): array
    {
        $fromNumber = getenv('TELNYX_PHONE_NUMBER');
        $connectionId = getenv('TELNYX_CONNECTION_ID');

        if (!$fromNumber || !$connectionId) {
            throw new \RuntimeException('Missing required environment variables: TELNYX_PHONE_NUMBER or TELNYX_CONNECTION_ID');
        }

        if (!str_starts_with($toNumber, '+')) {
            throw new \InvalidArgumentException('Phone number must be in E.164 format (e.g., +15551234567)');
        }

        $response = $this->client->calls->dial(
            from_: $fromNumber,
            to: $toNumber,
            connection_id: $connectionId,
        );

        $callControlId = $response->data->call_control_id;

        CallAnalytic::create([
            'call_control_id' => $callControlId,
            'from_number' => $fromNumber,
            'to_number' => $toNumber,
            'status' => 'initiated',
            'initiated_at' => Carbon::now(),
            'metadata' => [
                'initiated_via' => 'api',
            ],
        ]);

        return [
            'call_control_id' => $callControlId,
            'from' => $fromNumber,
            'to' => $toNumber,
            'status' => 'initiated',
        ];
    }

    public function getCallStatus(string $callControlId): array
    {
        $response = $this->client->calls->retrieve_status($callControlId);

        $call = CallAnalytic::where('call_control_id', $callControlId)->first();

        return [
            'call_control_id' => $response->data->call_control_id,
            'is_alive' => $response->data->is_alive,
            'status' => $call?->status ?? 'unknown',
            'duration_seconds' => $call?->duration_seconds,
            'initiated_at' => $call?->initiated_at,
            'answered_at' => $call?->answered_at,
        ];
    }

    public function hangupCall(string $callControlId): array
    {
        $response = $this->client->calls->actions->hangup($callControlId);

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'hangup_requested',
        ];
    }

    public function getAnalyticsSummary(string $startDate, string $endDate): array
    {
        $calls = CallAnalytic::whereBetween('initiated_at', [
            Carbon::parse($startDate)->startOfDay(),
            Carbon::parse($endDate)->endOfDay(),
        ])->get();

        $totalCalls = $calls->count();
        $completedCalls = $calls->where('status', 'completed')->count();
        $failedCalls = $calls->where('status', 'failed')->count();
        $totalDuration = $calls->sum('duration_seconds') ?? 0;
        $averageDuration = $totalCalls > 0 ? $totalDuration / $totalCalls : 0;

        return [
            'period' => [
                'start' => $startDate,
                'end' => $endDate,
            ],
            'total_calls' => $totalCalls,
            'completed_calls' => $completedCalls,
            'failed_calls' => $failedCalls,
            'success_rate' => $totalCalls > 0 ? round(($completedCalls / $totalCalls) * 100, 2) : 0,
            'total_duration_seconds' => $totalDuration,
            'average_duration_seconds' => round($averageDuration, 2),
        ];
    }
}

// app/Http/Controllers/CallController.php
namespace App\Http\Controllers;

use App\Services\CallService;
use Telnyx\Exception\ApiException;
use Telnyx\Exception\AuthenticationException;
use Telnyx\Exception\RateLimitException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CallController extends Controller
{
    private CallService $callService;

    public function __construct(CallService $callService)
    {
        $this->callService = $callService;
    }

    public function initiate(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'to' => 'required|string|regex:/^\+\d{10,15}$/',
        ]);

        try {
            $result = $this->callService->initiateCall($validated['to']);
            return response()->json($result, 201);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (RateLimitException) {
            return response()->json(['error' => 'Rate limit exceeded'], 429);
        } catch (ApiException $e) {
            return response()->json(['error' => $e->getMessage()], $e->getHttpStatus() ?? 400);
        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    public function status(string $callControlId): JsonResponse
    {
        try {
            $result = $this->callService->getCallStatus($callControlId);
            return response()->json($result, 200);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(['error' => $e->getMessage()], $e->getHttpStatus() ?? 400);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    public function hangup(string $callControlId): JsonResponse
    {
        try {
            $result = $this->callService->hangupCall($callControlId);
            return response()->json($result, 200);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(['error' => $e->getMessage()], $e->getHttpStatus() ?? 400);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    public function analytics(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'start_date' => 'required|date',
            'end_date' => 'required|date|after_or_equal:start_date',
        ]);

        try {
            $result = $this->callService->getAnalyticsSummary(
                $validated['start_date'],
                $validated['end_date']
            );
            return response()->json($result, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }
}

// app/Http/Controllers/WebhookController.php
namespace App\Http\Controllers;

use App\Models\CallAnalytic;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class WebhookController extends Controller
{
    public function handleCallEvent(Request $request): JsonResponse
    {
        $payload = $request->all();

        $eventType = $payload['data']['event_type'] ?? null;
        $callControlId = $payload['data']['call_control_id'] ?? null;

        if (!$callControlId) {
            return response()->json(['error' => 'Missing call_control_id'], 400);
        }

        $call = CallAnalytic::where('call_control_id', $callControlId)->first();

        if (!$call) {
            return response()->json(['error' => 'Call not found'], 404);
        }

        match ($eventType) {
            'call.initiated' => $this->handleCallInitiated($call, $payload),
            'call.answered' => $this->handleCallAnswered($call, $payload),
            'call.hangup' => $this->handleCallHangup($call, $payload),
            default => null,
        };

        return response()->json(['status' => 'received'], 200);
    }

    private function handleCallInitiated(CallAnalytic $call, array $payload): void
    {
        $call->update([
            'status' => 'initiated',
            'metadata' => array_merge($call->metadata ?? [], [
                'initiated_timestamp' => $payload['data']['occurred_at'] ?? null,
            ]),
        ]);
    }

    private function handleCallAnswered(CallAnalytic $call, array $payload): void
    {
        $call->update([
            'status' => 'answered',
            'answered_at' => Carbon::now(),
            'metadata' => array_merge($call->metadata ?? [], [
                'answered_timestamp' => $payload['data']['occurred_at'] ?? null,
            ]),
        ]);
    }

    private function handleCallHangup(CallAnalytic $call, array $payload): void
    {
        $endedAt = Carbon::now();
        $durationSeconds = $call->initiated_at
            ? $endedAt->diffInSeconds($call->initiated_at)
            : 0;

        $call->update([
            'status' => 'completed',
            'ended_at' => $endedAt,
            'duration_seconds' => $durationSeconds,
            'metadata' => array_merge($call->metadata ?? [], [
                'hangup_timestamp' => $payload['data']['occurred_at'] ?? null,
                'hangup_reason' => $payload['data']['hangup_reason'] ?? null,
            ]),
        ]);
    }
}

// routes/api.php
use App\Http\Controllers\CallController;
use App\Http\Controllers\WebhookController;
use Illuminate\Support\Facades\Route;

Route::post('/calls/initiate', [CallController::class, 'initiate']);
Route::get('/calls/{callControlId}/status', [CallController::class, 'status']);
Route::post('/calls/{callControlId}/hangup', [CallController::class, 'hangup']);
Route::get('/analytics', [CallController::class, 'analytics']);

Route::post('/webhooks/call', [WebhookController::class, 'handleCallEvent']);
