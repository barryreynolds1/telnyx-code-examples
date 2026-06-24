<?php
// app/Services/CallControlService.php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class CallControlService
{
    private Client $client;
    private string $phoneNumber;
    private string $connectionId;

    public function __construct()
    {
        $this->client = new Client(apiKey: env('TELNYX_API_KEY'));
        $this->phoneNumber = env('TELNYX_PHONE_NUMBER');
        $this->connectionId = env('TELNYX_CONNECTION_ID');
    }

    public function initiateCall(string $toNumber): array
    {
        $response = $this->client->calls->dial(
            from_: $this->phoneNumber,
            to: $toNumber,
            connection_id: $this->connectionId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'initiated',
        ];
    }

    public function answerCall(string $callControlId): array
    {
        $response = $this->client->calls->actions->answer(
            call_control_id: $callControlId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'answered',
        ];
    }

    public function holdCall(string $callControlId): array
    {
        $response = $this->client->calls->actions->hold(
            call_control_id: $callControlId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'held',
        ];
    }

    public function resumeCall(string $callControlId): array
    {
        $response = $this->client->calls->actions->resume(
            call_control_id: $callControlId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'resumed',
        ];
    }

    public function transferCall(string $originalCallId, string $transferCallId): array
    {
        $response = $this->client->calls->actions->transfer(
            call_control_id: $originalCallId,
            transfer_control_id: $transferCallId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'transferred',
        ];
    }

    public function hangupCall(string $callControlId): array
    {
        $response = $this->client->calls->actions->hangup(
            call_control_id: $callControlId,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'hung_up',
        ];
    }

    public function speakToCall(string $callControlId, string $text): array
    {
        $response = $this->client->calls->actions->speak(
            call_control_id: $callControlId,
            payload: $text,
        );

        return [
            'call_control_id' => $response->data->call_control_id,
            'status' => 'speaking',
        ];
    }
}

// app/Http/Controllers/WarmTransferController.php

namespace App\Http\Controllers;

use App\Models\WarmTransfer;
use App\Services\CallControlService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;

class WarmTransferController extends Controller
{
    private CallControlService $callControl;

    public function __construct(CallControlService $callControl)
    {
        $this->callControl = $callControl;
    }

    public function initiateTransfer(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'original_call_id' => 'required|string',
            'transfer_to' => 'required|string|starts_with:+',
        ]);

        try {
            $this->callControl->holdCall($validated['original_call_id']);

            $dialResponse = $this->callControl->initiateCall($validated['transfer_to']);
            $transferCallId = $dialResponse['call_control_id'];

            $transfer = WarmTransfer::create([
                'original_call_id' => $validated['original_call_id'],
                'transfer_call_id' => $transferCallId,
                'transfer_recipient' => $validated['transfer_to'],
                'status' => 'transfer_dialing',
            ]);

            return response()->json([
                'transfer_id' => $transfer->id,
                'original_call_id' => $validated['original_call_id'],
                'transfer_call_id' => $transferCallId,
                'status' => 'transfer_dialing',
            ], 200);

        } catch (ApiException $e) {
            return response()->json([
                'error' => 'Failed to initiate transfer',
                'details' => $e->getMessage(),
            ], $e->getHttpStatus() ?? 500);
        }
    }

    public function completeTransfer(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'original_call_id' => 'required|string',
            'transfer_call_id' => 'required|string',
        ]);

        try {
            $this->callControl->transferCall(
                $validated['original_call_id'],
                $validated['transfer_call_id']
            );

            WarmTransfer::where('original_call_id', $validated['original_call_id'])
                ->update(['status' => 'transferred']);

            return response()->json([
                'original_call_id' => $validated['original_call_id'],
                'transfer_call_id' => $validated['transfer_call_id'],
                'status' => 'transferred',
            ], 200);

        } catch (ApiException $e) {
            return response()->json([
                'error' => 'Failed to complete transfer',
                'details' => $e->getMessage(),
            ], $e->getHttpStatus() ?? 500);
        }
    }

    public function cancelTransfer(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'original_call_id' => 'required|string',
            'transfer_call_id' => 'required|string',
        ]);

        try {
            $this->callControl->hangupCall($validated['transfer_call_id']);

            $this->callControl->resumeCall($validated['original_call_id']);

            WarmTransfer::where('original_call_id', $validated['original_call_id'])
                ->update(['status' => 'failed']);

            return response()->json([
                'original_call_id' => $validated['original_call_id'],
                'status' => 'cancelled',
            ], 200);

        } catch (ApiException $e) {
            return response()->json([
                'error' => 'Failed to cancel transfer',
                'details' => $e->getMessage(),
            ], $e->getHttpStatus() ?? 500);
        }
    }
}

// app/Http/Controllers/WebhookController.php

namespace App\Http\Controllers;

use App\Models\WarmTransfer;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class WebhookController extends Controller
{
    public function handleCallEvent(Request $request): JsonResponse
    {
        $event = $request->input('data.event_type');
        $callControlId = $request->input('data.payload.call_control_id');

        \Log::info('Telnyx webhook event', [
            'event' => $event,
            'call_control_id' => $callControlId,
        ]);

        if ($event === 'call.answered') {
            $transfer = WarmTransfer::where('transfer_call_id', $callControlId)->first();
            if ($transfer) {
                $transfer->update(['status' => 'transfer_answered']);
            }
        }

        if ($event === 'call.hangup') {
            WarmTransfer::where('original_call_id', $callControlId)
                ->orWhere('transfer_call_id', $callControlId)
                ->delete();
        }

        return response()->json(['status' => 'received'], 200);
    }
}

// routes/api.php

use App\Http\Controllers\WarmTransferController;
use App\Http\Controllers\WebhookController;
use Illuminate\Support\Facades\Route;

Route::post('/warm-transfer/initiate', [WarmTransferController::class, 'initiateTransfer']);
Route::post('/warm-transfer/complete', [WarmTransferController::class, 'completeTransfer']);
Route::post('/warm-transfer/cancel', [WarmTransferController::class, 'cancelTransfer']);

Route::post('/webhooks/call-events', [WebhookController::class, 'handleCallEvent']);
