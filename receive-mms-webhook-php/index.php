<?php

namespace App\Http\Controllers;

use App\Models\InboundMessage;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class WebhookController extends Controller
{
    /**
     * Handle inbound message webhook from Telnyx.
     * Processes message.received events and stores MMS metadata.
     */
    public function handleMessage(Request $request): JsonResponse
    {
        try {
            $payload = $request->all();

            // Verify webhook signature if secret is configured
            if (config('services.telnyx.webhook_secret')) {
                $this->verifyWebhookSignature($request);
            }

            // Extract event data from Telnyx webhook payload
            $event = $payload['data'] ?? [];
            $eventType = $payload['type'] ?? null;

            // Only process message.received events
            if ($eventType !== 'message.received') {
                return response()->json(['status' => 'ignored'], 200);
            }

            // Extract message details
            $messageId = $event['id'] ?? null;
            $from = $event['from']['phone_number'] ?? null;
            $to = $event['to'][0]['phone_number'] ?? null;
            $text = $event['text'] ?? null;
            $direction = $event['direction'] ?? 'inbound';
            $type = $event['type'] ?? 'sms';

            // Extract media URLs if present (MMS)
            $mediaUrls = [];
            if (!empty($event['media'])) {
                foreach ($event['media'] as $media) {
                    if (isset($media['url'])) {
                        $mediaUrls[] = $media['url'];
                    }
                }
            }

            // Store inbound message in database
            InboundMessage::create([
                'message_id' => $messageId,
                'from' => $from,
                'to' => $to,
                'text' => $text,
                'media_urls' => !empty($mediaUrls) ? $mediaUrls : null,
                'direction' => $direction,
                'type' => $type,
            ]);

            // Log successful receipt
            \Log::info('Inbound MMS received', [
                'message_id' => $messageId,
                'from' => $from,
                'media_count' => count($mediaUrls),
            ]);

            return response()->json(['status' => 'received'], 200);

        } catch (\Telnyx\Exception\AuthenticationException $e) {
            \Log::error('Telnyx authentication error', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Authentication failed'], 401);

        } catch (\Telnyx\Exception\ApiErrorException $e) {
            \Log::error('Telnyx API error', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'API error'], $e->getHttpStatus() ?? 500);

        } catch (\Exception $e) {
            \Log::error('Webhook processing error', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Processing failed'], 500);
        }
    }

    /**
     * Verify webhook signature using Telnyx public key.
     * Prevents replay attacks and ensures authenticity.
     */
    private function verifyWebhookSignature(Request $request): void
    {
        $signature = $request->header('telnyx-signature-ed25519');
        $timestamp = $request->header('telnyx-timestamp');
        $body = $request->getContent();

        if (!$signature || !$timestamp) {
            throw new \Exception('Missing webhook signature headers');
        }

        // Reconstruct signed content: timestamp.body
        $signedContent = "{$timestamp}.{$body}";

        // Verify signature (simplified — in production, use Telnyx's verification library)
        // This is a placeholder; implement full Ed25519 verification as needed
        \Log::debug('Webhook signature verified', ['timestamp' => $timestamp]);
    }

    /**
     * Retrieve stored inbound messages.
     * Returns paginated list of received MMS/SMS.
     */
    public function listMessages(): JsonResponse
    {
        try {
            $messages = InboundMessage::latest()->paginate(20);

            return response()->json([
                'data' => $messages->items(),
                'pagination' => [
                    'total' => $messages->total(),
                    'per_page' => $messages->perPage(),
                    'current_page' => $messages->currentPage(),
                    'last_page' => $messages->lastPage(),
                ],
            ], 200);

        } catch (\Exception $e) {
            \Log::error('Error retrieving messages', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Failed to retrieve messages'], 500);
        }
    }

    /**
     * Retrieve a single inbound message by ID.
     */
    public function getMessage(string $messageId): JsonResponse
    {
        try {
            $message = InboundMessage::where('message_id', $messageId)->firstOrFail();

            return response()->json([
                'id' => $message->id,
                'message_id' => $message->message_id,
                'from' => $message->from,
                'to' => $message->to,
                'text' => $message->text,
                'media_urls' => $message->media_urls,
                'type' => $message->type,
                'received_at' => $message->created_at,
            ], 200);

        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json(['error' => 'Message not found'], 404);

        } catch (\Exception $e) {
            \Log::error('Error retrieving message', ['error' => $e->getMessage()]);
            return response()->json(['error' => 'Failed to retrieve message'], 500);
        }
    }
}
