<?php
// app/Services/VoicemailService.php

namespace App\Services;

use App\Models\Voicemail;
use Telnyx\Client;
use Telnyx\Exception\ApiErrorException;

class VoicemailService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: config('telnyx.api_key'));
    }

    public function answerAndRecord(string $callControlId): array
    {
        try {
            $this->client->calls->actions->answer($callControlId, []);

            $this->client->calls->actions->speak(
                $callControlId,
                [
                    'payload' => 'Please leave your message after the beep.',
                    'language' => 'en-US',
                    'voice' => 'female',
                ]
            );

            $recordingResponse = $this->client->calls->actions->startRecording(
                $callControlId,
                [
                    'format' => 'wav',
                    'channels' => 'mono',
                ]
            );

            return [
                'success' => true,
                'message' => 'Call answered and recording started',
                'recording_id' => $recordingResponse->data->recordingId ?? null,
            ];
        } catch (ApiErrorException $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'status_code' => $e->getHttpStatus(),
            ];
        }
    }

    public function stopRecordingAndHangup(string $callControlId): array
    {
        try {
            $this->client->calls->actions->stopRecording($callControlId, []);
            $this->client->calls->actions->hangup($callControlId, []);

            return [
                'success' => true,
                'message' => 'Recording stopped and call ended',
            ];
        } catch (ApiErrorException $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'status_code' => $e->getHttpStatus(),
            ];
        }
    }

    public function getCallStatus(string $callControlId): array
    {
        try {
            $response = $this->client->calls->retrieveStatus($callControlId);

            return [
                'call_control_id' => $response->data->callControlId,
                'is_alive' => $response->data->isAlive,
                'state' => $response->data->state ?? 'unknown',
            ];
        } catch (ApiErrorException $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'status_code' => $e->getHttpStatus(),
            ];
        }
    }

    public function createVoicemailRecord(array $data): Voicemail
    {
        return Voicemail::create($data);
    }

    public function updateVoicemailRecord(string $callControlId, array $data): ?Voicemail
    {
        Voicemail::where('call_control_id', $callControlId)->update($data);
        return Voicemail::where('call_control_id', $callControlId)->first();
    }

    public function getAllVoicemails(): array
    {
        return Voicemail::orderBy('created_at', 'desc')->get()->toArray();
    }

    public function getVoicemailById(int $id): ?array
    {
        $voicemail = Voicemail::find($id);
        return $voicemail ? $voicemail->toArray() : null;
    }
}

// app/Http/Controllers/WebhookController.php

namespace App\Http\Controllers;

use App\Models\Voicemail;
use App\Services\VoicemailService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class WebhookController extends Controller
{
    private VoicemailService $voicemailService;

    public function __construct(VoicemailService $voicemailService)
    {
        $this->voicemailService = $voicemailService;
    }

    public function handleVoiceWebhook(Request $request): JsonResponse
    {
        try {
            $payload = $request->json()->all();
            $eventType = $payload['data']['event_type'] ?? null;
            $callControlId = $payload['data']['call_control_id'] ?? null;

            if (!$callControlId) {
                return response()->json(['error' => 'Missing call_control_id'], 400);
            }

            match ($eventType) {
                'call.initiated' => $this->handleCallInitiated($payload),
                'call.answered' => $this->handleCallAnswered($payload),
                'call.hangup' => $this->handleCallHangup($payload),
                'call.recording.saved' => $this->handleRecordingSaved($payload),
                default => null,
            };

            return response()->json(['status' => 'received'], 200);
        } catch (\Exception $e) {
            \Log::error('Webhook error: ' . $e->getMessage());
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    private function handleCallInitiated(array $payload): void
    {
        $data = $payload['data'];
        $callControlId = $data['call_control_id'];
        $fromNumber = $data['from'] ?? 'unknown';
        $toNumber = $data['to'] ?? config('telnyx.phone_number');

        $this->voicemailService->createVoicemailRecord([
            'call_control_id' => $callControlId,
            'from_number' => $fromNumber,
            'to_number' => $toNumber,
            'status' => 'initiated',
        ]);
    }

    private function handleCallAnswered(array $payload): void
    {
        $callControlId = $payload['data']['call_control_id'];

        $result = $this->voicemailService->answerAndRecord($callControlId);

        if ($result['success']) {
            $this->voicemailService->updateVoicemailRecord($callControlId, [
                'status' => 'recording',
                'recording_id' => $result['recording_id'] ?? null,
            ]);
        }
    }

    private function handleCallHangup(array $payload): void
    {
        $callControlId = $payload['data']['call_control_id'];

        $this->voicemailService->stopRecordingAndHangup($callControlId);

        $this->voicemailService->updateVoicemailRecord($callControlId, [
            'status' => 'completed',
        ]);
    }

    private function handleRecordingSaved(array $payload): void
    {
        $data = $payload['data'];
        $callControlId = $data['call_control_id'];
        $recordingUrl = $data['recording_url'] ?? null;
        $durationSeconds = $data['duration_seconds'] ?? null;

        $this->voicemailService->updateVoicemailRecord($callControlId, [
            'recording_url' => $recordingUrl,
            'duration_seconds' => $durationSeconds,
        ]);
    }
}

// app/Http/Controllers/VoicemailController.php

namespace App\Http\Controllers;

use App\Services\VoicemailService;
use Illuminate\Http\JsonResponse;

class VoicemailController extends Controller
{
    private VoicemailService $voicemailService;

    public function __construct(VoicemailService $voicemailService)
    {
        $this->voicemailService = $voicemailService;
    }

    public function index(): JsonResponse
    {
        try {
            $voicemails = $this->voicemailService->getAllVoicemails();
            return response()->json($voicemails, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function show(int $id): JsonResponse
    {
        try {
            $voicemail = $this->voicemailService->getVoicemailById($id);

            if (!$voicemail) {
                return response()->json(['error' => 'Voicemail not found'], 404);
            }

            return response()->json($voicemail, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}

// routes/api.php

use App\Http\Controllers\WebhookController;
use App\Http\Controllers\VoicemailController;
use Illuminate\Support\Facades\Route;

Route::post('/webhooks/voice', [WebhookController::class, 'handleVoiceWebhook']);

Route::get('/voicemails', [VoicemailController::class, 'index']);
Route::get('/voicemails/{id}', [VoicemailController::class, 'show']);

// config/telnyx.php

return [
    'api_key' => env('TELNYX_API_KEY'),
    'phone_number' => env('TELNYX_PHONE_NUMBER'),
    'connection_id' => env('TELNYX_CONNECTION_ID'),
    'webhook_url' => env('WEBHOOK_URL'),
];

// .env

TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE
WEBHOOK_URL=https://your-domain.com/api/webhooks/voice
