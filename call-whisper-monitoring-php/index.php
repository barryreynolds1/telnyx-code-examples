<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Telnyx\Client;
use Telnyx\Exception\ApiErrorException;

class CallController extends Controller
{
    private Client $client;

    public function __construct()
    {
        // Initialize Telnyx client with API key from environment
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    /**
     * Initiate an outbound call with a whisper prompt.
     * The whisper prompt is played to the caller before the call connects.
     */
    public function initiateCall(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'to' => 'required|string|regex:/^\+\d{1,15}$/',
            'whisper_text' => 'required|string|max:500',
        ]);

        $toNumber = $validated['to'];
        $whisperText = $validated['whisper_text'];
        $fromNumber = config('services.telnyx.phone_number');
        $connectionId = config('services.telnyx.connection_id');

        try {
            // Initiate the call using the Telnyx SDK
            $response = $this->client->calls->dial(
                from_: $fromNumber,
                to: $toNumber,
                connection_id: $connectionId,
                custom_headers: [
                    [
                        'name' => 'X-Whisper-Text',
                        'value' => $whisperText,
                    ],
                ],
            );

            // Extract and return serializable call data
            return response()->json([
                'call_control_id' => $response->data->call_control_id,
                'from' => $fromNumber,
                'to' => $toNumber,
                'whisper_text' => $whisperText,
                'status' => 'initiated',
            ], 201);

        } catch (ApiErrorException $e) {
            // Handle Telnyx API errors
            return $this->handleApiError($e);
        }
    }

    /**
     * Handle incoming webhook events from Telnyx.
     * Events include: call.initiated, call.answered, call.hangup, etc.
     */
    public function handleWebhook(Request $request): JsonResponse
    {
        $event = $request->input('data.event_type');
        $callControlId = $request->input('data.payload.call_control_id');

        // Log the event for debugging
        \Log::info('Telnyx webhook received', [
            'event' => $event,
            'call_control_id' => $callControlId,
        ]);

        switch ($event) {
            case 'call.initiated':
                return $this->handleCallInitiated($request);
            case 'call.answered':
                return $this->handleCallAnswered($request);
            case 'call.hangup':
                return $this->handleCallHangup($request);
            default:
                return response()->json(['status' => 'acknowledged'], 200);
        }
    }

    /**
     * Handle call.initiated event — call has been created.
     */
    private function handleCallInitiated(Request $request): JsonResponse
    {
        $callControlId = $request->input('data.payload.call_control_id');
        $from = $request->input('data.payload.from.phone_number');
        $to = $request->input('data.payload.to.phone_number');

        \Log::info('Call initiated', [
            'call_control_id' => $callControlId,
            'from' => $from,
            'to' => $to,
        ]);

        return response()->json(['status' => 'acknowledged'], 200);
    }

    /**
     * Handle call.answered event — recipient has answered.
     * Play the whisper prompt to the caller.
     */
    private function handleCallAnswered(Request $request): JsonResponse
    {
        $callControlId = $request->input('data.payload.call_control_id');
        $whisperText = $request->input('data.payload.custom_headers.0.value', 'Hello, your call is connected.');

        try {
            // Speak the whisper prompt to the caller
            $this->client->calls->actions->speak(
                call_control_id: $callControlId,
                payload: [
                    'text' => $whisperText,
                    'language' => 'en-US',
                    'voice' => 'female',
                ],
            );

            \Log::info('Whisper prompt played', [
                'call_control_id' => $callControlId,
                'text' => $whisperText,
            ]);

        } catch (ApiErrorException $e) {
            \Log::error('Failed to play whisper prompt', [
                'call_control_id' => $callControlId,
                'error' => $e->getMessage(),
            ]);
        }

        return response()->json(['status' => 'acknowledged'], 200);
    }

    /**
     * Handle call.hangup event — call has ended.
     */
    private function handleCallHangup(Request $request): JsonResponse
    {
        $callControlId = $request->input('data.payload.call_control_id');
        $hangupReason = $request->input('data.payload.hangup_reason', 'unknown');

        \Log::info('Call ended', [
            'call_control_id' => $callControlId,
            'reason' => $hangupReason,
        ]);

        return response()->json(['status' => 'acknowledged'], 200);
    }

    /**
     * Handle Telnyx API errors and map to HTTP status codes.
     */
    private function handleApiError(ApiErrorException $e): JsonResponse
    {
        $statusCode = $e->getHttpStatus() ?? 500;
        $message = $e->getMessage();

        // Map common Telnyx errors to HTTP status codes
        if (str_contains($message, 'Unauthorized')) {
            $statusCode = 401;
            $message = 'Invalid API key';
        } elseif (str_contains($message, 'Rate limit')) {
            $statusCode = 429;
            $message = 'Rate limit exceeded. Please slow down.';
        }

        return response()->json([
            'error' => $message,
            'status_code' => $statusCode,
        ], $statusCode);
    }
}
