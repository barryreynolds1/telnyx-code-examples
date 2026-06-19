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
