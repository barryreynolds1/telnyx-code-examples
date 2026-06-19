# Chat With AI Assistant with PHP and Laravel

## What Does This Example Do?

Build a production-ready Laravel application that enables real-time chat interactions with Telnyx AI Assistants. This tutorial demonstrates the PHP SDK client initialization pattern, proper error handling for AI API responses, and secure credential management via environment variables. You'll create a web interface and backend API endpoint that sends user messages to an AI Assistant and streams responses back.

## Who Is This For?

- **PHP developers** building ai features with Laravel.
- **Backend engineers** integrating telephony or messaging into existing applications.
- **DevOps teams** looking for containerized, production-ready telecom examples.
- **Startups and enterprises** replacing legacy telecom providers with a modern API-first platform.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that gives developers a single API for [voice](https://telnyx.com/products/voice-ai-agents), [messaging](https://telnyx.com/products/sms-api), [SIP](https://telnyx.com/products/sip-trunks), [AI](https://telnyx.com/ai-assistants), and [IoT](https://telnyx.com/products/iot-sim-card) — no Frankenstack required.

- **Integrated platform** — [Voice](https://telnyx.com/products/voice-ai-agents), [SMS](https://telnyx.com/products/sms-api), [SIP trunking](https://telnyx.com/products/sip-trunks), [AI assistants](https://telnyx.com/ai-assistants), and [IoT SIM management](https://telnyx.com/products/iot-sim-card) under one roof. No stitching together multiple vendors.
- **Global private network** — Calls and messages traverse the Telnyx-owned IP network for lower latency and higher reliability than the public internet.
- **Developer-first** — SDKs for Python, Node.js, Go, Ruby, Java, and PHP. Comprehensive webhook event model. Sandbox environment for testing.
- **Competitive pricing** — Pay-as-you-go with no minimums, contracts, or per-seat fees.

## Prerequisites

- PHP 8.1 or higher.
- Laravel 10 or higher.
- Composer (PHP package manager).
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- An existing AI Assistant ID (create one via the Telnyx Portal or use the [Create AI Assistant](/tutorials/ai/php/create-ai-assistant) tutorial).
- A publicly accessible URL for webhook testing (optional, for advanced features).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-php
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-php
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a controller to handle chat interactions. Generate the controller:

```bash
php artisan make:controller ChatController
```

Edit `app/Http/Controllers/ChatController.php`:

```php
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
```

Create a Blade view for the chat interface. First, create the directory:

```bash
mkdir -p resources/views/chat
```

Create `resources/views/chat/index.blade.php`:

```blade
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 600px;
            display: flex;
            flex-direction: column;
            height: 600px;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            display: flex;
            gap: 10px;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
            line-height: 1.4;
        }

        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-content {
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 4px;
        }

        .message-time {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }

        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }

        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        .input-area input:focus {
            outline: none;
            border-color: #667eea;
        }

        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }

        .input-area button:hover {
            background: #5568d3;
        }

        .input-area button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 10px 20px 0;
            font-size: 14px;
        }

        .loading {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
            margin-right: 5px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>AI Assistant Chat</h1>
            <p>Powered by Telnyx</p>
        </div>

        <div class="messages" id="messages"></div>

        <div id="error" class="error" style="display: none;"></div>

        <div class="input-area">
            <input 
                type="text" 
                id="messageInput" 
                placeholder="Type your message..." 
                autocomplete="off"
            >
            <button id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const errorDiv = document.getElementById('error');

        // Allow sending message with Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                sendMessage();
            }
        });

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Disable input while sending
            sendBtn.disabled = true;
            messageInput.disabled = true;
            errorDiv.style.display = 'none';

            // Display user message immediately
            displayMessage(message, 'user');
            messageInput.value = '';

            try {
                // Send message to backend API
                const response = await fetch('/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || '',
                    },
                    body: JSON.stringify({ message }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to get response');
                }

                // Display assistant response
                displayMessage(data.assistant_message, 'assistant');

            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            } finally {
                // Re-enable input
                sendBtn.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        }

        function displayMessage(text, role) {
            const messageEl = document.createElement('div');
            messageEl.className = `message ${role}`;

            const contentEl = document.createElement('div');
            contentEl.className = 'message-content';
            contentEl.textContent = text;

            const timeEl = document.createElement('div');
            timeEl.className = 'message-time';
            timeEl.textContent = new Date().toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });

            messageEl.appendChild(contentEl);
            messageEl.appendChild(timeEl);
            messagesDiv.appendChild(messageEl);

            // Auto-scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    </script>
</body>
</html>
```

Add CSRF token to the view. Update `resources/views/chat/index.blade.php` head section to include:

```blade
<meta name="csrf-token" content="{{ csrf_token() }}">
```

Define routes in `routes/web.php`:

```php
<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ChatController;

Route::get('/', [ChatController::class, 'index']);
Route::get('/chat', [ChatController::class, 'index']);
Route::post('/chat/send', [ChatController::class, 'sendMessage']);
Route::get('/chat/assistant-info', [ChatController::class, 'getAssistantInfo']);
```

## Complete Code

See [`index.php`](./index.php) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"success": false, "error": "Authentication failed. Check your API key."}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the Laravel development server after updating the `.env` file. Run `php artisan config:clear` to clear cached configuration. |
| Assistant ID Not Found | The API returns a 404 error or "Assistant not found" message. | Confirm that `TELNYX_AI_ASSISTANT_ID` in your `.env` file is correct and matches an existing assistant in your Telnyx account. Verify the assistant ID format (typically a UUID). Create a new assistant via the [Telnyx Portal](https://portal.telnyx.com) if needed, then update your `.env` file with the new ID. |
| CSRF Token Mismatch | The POST request fails with a 419 error or "CSRF token mismatch" message. | Ensure the `X-CSRF-TOKEN` header is included in your API requests. The Blade template automatically includes `{{ csrf_token() }}` in a meta tag. If testing with curl, extract the token from the HTML response or disable CSRF for testing routes in `app/Http/Middleware/VerifyCsrfToken.php` (not recommended for production). |
| Rate Limit Exceeded (429) | The endpoint returns `{"success": false, "error": "Rate limit exceeded..."}` with HTTP 429. | Implement exponential backoff in your client code. Wait at least 1 second between requests. If sending many messages, consider implementing a queue system using Laravel's job queue. Check your Telnyx account plan for rate limit details in the [Portal](https://portal.telnyx.com). |
| Network Error (503) | The endpoint returns `{"success": false, "error": "Network error connecting to Telnyx..."}` with HTTP 503. | Verify your internet connection and that the Telnyx API is accessible. Check if your firewall or proxy blocks outbound HTTPS requests to `api.telnyx.com`. Temporarily disable VPN or proxy services if applicable. Retry the request after a few seconds. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this AI example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What PHP version do I need?**

PHP 8.1 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [AI Assistants Guide](https://developers.telnyx.com/docs/inference/ai-assistants/no-code-voice-assistant)
- [Assistants API Reference](https://developers.telnyx.com/api-reference/assistants/create-an-assistant)
- [PHP SDK](https://developers.telnyx.com/development/sdk/php)
- [Telnyx AI Assistants](https://telnyx.com/ai-assistants)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [List All AI Assistants](/tutorials/ai/php/list-ai-assistants).
- [Create an AI Assistant](/tutorials/ai/php/create-ai-assistant).
- [Update an AI Assistant](/tutorials/ai/php/update-ai-assistant).
