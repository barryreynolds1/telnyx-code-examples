<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Telnyx\Client;
use Telnyx\Exception\ApiErrorException;

class ChatController extends Controller
{
    private Client $client;
    private string $assistantId;

    public function __construct()
    {
        // Initialize Telnyx client with API key from environment
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
        $this->assistantId = config('services.telnyx.assistant_id');
    }

    /**
     * Display the chat interface.
     */
    public function index()
    {
        return view('chat.index');
    }

    /**
     * Send a message to the AI Assistant and return the response.
     * 
     * Accepts JSON POST request with 'message' field.
     * Returns JSON response with assistant's reply.
     */
    public function sendMessage(Request $request): JsonResponse
    {
        // Validate incoming request
        $validated = $request->validate([
            'message' => 'required|string|max:2000',
        ]);

        $userMessage = $validated['message'];

        try {
            // Call the AI Assistant chat endpoint
            // The client.ai_assistants.chat() method sends the message and receives a response
            $response = $this->client->aiAssistants->chat(
                $this->assistantId,
                [
                    'messages' => [
                        [
                            'role' => 'user',
                            'content' => $userMessage,
                        ],
                    ],
                ]
            );

            // Extract serializable data from the SDK response object
            // SDK objects are NOT JSON-serializable, so we unpack to plain arrays
            $assistantMessage = $response->data->result->output ?? 'No response received';

            return response()->json([
                'success' => true,
                'user_message' => $userMessage,
                'assistant_message' => $assistantMessage,
                'timestamp' => now()->toIso8601String(),
            ], 200);

        } catch (\Telnyx\Exception\AuthenticationException $e) {
            // Invalid or missing API key
            return response()->json([
                'success' => false,
                'error' => 'Authentication failed. Check your API key.',
            ], 401);

        } catch (\Telnyx\Exception\RateLimitException $e) {
            // Rate limit exceeded
            return response()->json([
                'success' => false,
                'error' => 'Rate limit exceeded. Please wait before sending another message.',
            ], 429);

        } catch (ApiErrorException $e) {
            // General API error with status code
            $statusCode = $e->getHttpStatus() ?? 500;
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
                'status_code' => $statusCode,
            ], $statusCode);

        } catch (\Exception $e) {
            // Network or connection errors
            return response()->json([
                'success' => false,
                'error' => 'Network error connecting to Telnyx. Please try again.',
            ], 503);
        }
    }

    /**
     * Retrieve conversation history (optional enhancement).
     * 
     * This endpoint demonstrates retrieving assistant metadata.
     */
    public function getAssistantInfo(): JsonResponse
    {
        try {
            $response = $this->client->aiAssistants->retrieve($this->assistantId);

            // Extract serializable fields from the assistant object
            return response()->json([
                'id' => $response->data->id,
                'name' => $response->data->name,
                'model' => $response->data->model,
                'enabled_features' => $response->data->enabledFeatures ?? [],
            ], 200);

        } catch (\Telnyx\Exception\AuthenticationException $e) {
            return response()->json([
                'success' => false,
                'error' => 'Authentication failed.',
            ], 401);

        } catch (ApiErrorException $e) {
            $statusCode = $e->getHttpStatus() ?? 500;
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], $statusCode);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Network error.',
            ], 503);
        }
    }
}
