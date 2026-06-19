<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Telnyx\Client;
use Telnyx\AuthenticationError;
use Telnyx\RateLimitError;
use Telnyx\APIStatusError;
use Telnyx\APIConnectionError;

class SmsController extends Controller
{
    public function send(Request $request): JsonResponse
    {
        // Validate request payload
        $validated = $request->validate([
            'to' => 'required|string',
            'message' => 'required|string|max:1600',
        ]);

        $toNumber = $validated['to'];
        $message = $validated['message'];
        $fromNumber = env('TELNYX_PHONE_NUMBER');

        if (!$fromNumber) {
            return response()->json(['error' => 'TELNYX_PHONE_NUMBER environment variable not set'], 500);
        }

        // Validate E.164 format to prevent API errors
        if (!str_starts_with($toNumber, '+')) {
            return response()->json(['error' => 'Phone number must be in E.164 format (e.g., +15551234567)'], 400);
        }

        try {
            // Initialize client using new pattern — NOT static setApiKey()
            $client = new Client(apiKey: env('TELNYX_API_KEY'));

            // Send message using client.messages->create()
            $response = $client->messages->create([
                'from' => $fromNumber,
                'to' => $toNumber,
                'text' => $message,
            ]);

            // Extract serializable data — do not return raw response object
            return response()->json([
                'message_id' => $response->id,
                'status' => $response->to[0]->status ?? 'unknown',
                'from' => $fromNumber,
                'to' => $toNumber,
            ]);

        } catch (AuthenticationError $e) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (RateLimitError $e) {
            return response()->json(['error' => 'Rate limit exceeded. Please slow down.'], 429);
        } catch (APIStatusError $e) {
            return response()->json(['error' => $e->getMessage(), 'status_code' => $e->getCode()], $e->getCode());
        } catch (APIConnectionError $e) {
            return response()->json(['error' => 'Network error connecting to Telnyx'], 503);
        }
    }
}
