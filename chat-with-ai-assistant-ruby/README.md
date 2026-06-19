# Chat With AI Assistant with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails application that enables real-time chat interactions with Telnyx AI Assistants. This tutorial demonstrates the Telnyx Ruby SDK initialization pattern, proper error handling for AI API calls, and secure credential management via environment variables. You'll create a Rails controller that accepts chat messages and streams responses from your configured AI Assistant.

## Who Is This For?

- **Ruby developers** building ai features with Rails.
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

- Ruby 3.0 or higher.
- Rails 6.0 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- An existing AI Assistant created in the Telnyx Portal (or create one via the API).
- Bundler (Ruby package manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle AI Assistant chat logic in `app/services/ai_chat_service.rb`:

```ruby
# app/services/ai_chat_service.rb
class AiChatService
  def initialize(assistant_id)
    @assistant_id = assistant_id
    @client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
  end

  def chat(messages)
    # Validate assistant ID is configured
    unless @assistant_id
      raise ArgumentError, "TELNYX_ASSISTANT_ID environment variable not set"
    end

    # Validate messages array is not empty
    if messages.blank? || !messages.is_a?(Array)
      raise ArgumentError, "Messages must be a non-empty array"
    end

    # Call the AI Assistant chat endpoint
    # messages format: [{ role: "user", content: "Hello" }]
    response = @client.ai_assistants.chat(
      @assistant_id,
      messages: messages
    )

    # Extract serializable data — SDK objects are NOT JSON-serializable
    {
      assistant_id: response.data.assistant_id,
      messages: response.data.messages.map do |msg|
        {
          role: msg.role,
          content: msg.content
        }
      end,
      created_at: response.data.created_at
    }
  end
end
```

Update the Rails controller in `app/controllers/chat_controller.rb`:

```ruby
# app/controllers/chat_controller.rb
class ChatController < ApplicationController
  skip_forgery_protection only: [:create]

  def index
    # Render the chat interface view
    render :index
  end

  def create
    # Extract messages from request body
    messages = params.require(:messages)

    unless messages.is_a?(Array) && messages.any?
      return render json: { error: "Messages array required and must not be empty" }, status: :bad_request
    end

    # Initialize the AI chat service with the configured assistant ID
    assistant_id = ENV["TELNYX_ASSISTANT_ID"]
    service = AiChatService.new(assistant_id)

    begin
      # Call the service to chat with the AI Assistant
      result = service.chat(messages)
      render json: result, status: :ok

    rescue Telnyx::AuthenticationError
      render json: { error: "Invalid API key" }, status: :unauthorized

    rescue Telnyx::RateLimitError
      render json: { error: "Rate limit exceeded. Please slow down." }, status: :too_many_requests

    rescue Telnyx::APIStatusError => e
      render json: { error: e.message, status_code: e.status_code }, status: e.status_code

    rescue Telnyx::APIConnectionError
      render json: { error: "Network error connecting to Telnyx" }, status: :service_unavailable

    rescue ArgumentError => e
      render json: { error: e.message }, status: :bad_request
    end
  end
end
```

Create a simple chat interface view in `app/views/chat/index.html.erb`:

```erb
<!-- app/views/chat/index.html.erb -->
<div class="chat-container">
  <h1>Chat with AI Assistant</h1>
  
  <div id="messages" class="messages-box"></div>
  
  <form id="chat-form">
    <input 
      type="text" 
      id="message-input" 
      placeholder="Type your message..." 
      required
    />
    <button type="submit">Send</button>
  </form>
</div>

<style>
  .chat-container {
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
  }
  
  .messages-box {
    border: 1px solid #ccc;
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #f9f9f9;
  }
  
  .message {
    margin: 10px 0;
    padding: 8px;
    border-radius: 4px;
  }
  
  .message.user {
    background-color: #e3f2fd;
    text-align: right;
  }
  
  .message.assistant {
    background-color: #f5f5f5;
  }
  
  form {
    display: flex;
    gap: 10px;
  }
  
  input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  button {
    padding: 8px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #0056b3;
  }
</style>

<script>
  const form = document.getElementById('chat-form');
  const input = document.getElementById('message-input');
  const messagesDiv = document.getElementById('messages');
  let conversationHistory = [];

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userMessage = input.value.trim();
    if (!userMessage) return;

    // Add user message to conversation history
    conversationHistory.push({ role: 'user', content: userMessage });

    // Display user message in UI
    const userMsgEl = document.createElement('div');
    userMsgEl.className = 'message user';
    userMsgEl.textContent = userMessage;
    messagesDiv.appendChild(userMsgEl);

    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
      // Send conversation history to backend
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({ messages: conversationHistory })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Chat failed');
      }

      const data = await response.json();

      // Update conversation history with assistant response
      if (data.messages && data.messages.length > 0) {
        const lastMessage = data.messages[data.messages.length - 1];
        if (lastMessage.role === 'assistant') {
          conversationHistory.push(lastMessage);

          // Display assistant message in UI
          const assistantMsgEl = document.createElement('div');
          assistantMsgEl.className = 'message assistant';
          assistantMsgEl.textContent = lastMessage.content;
          messagesDiv.appendChild(assistantMsgEl);
          messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
      }
    } catch (error) {
      const errorEl = document.createElement('div');
      errorEl.className = 'message';
      errorEl.style.color = 'red';
      errorEl.textContent = `Error: ${error.message}`;
      messagesDiv.appendChild(errorEl);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  });
</script>
```

Update your routes in `config/routes.rb`:

```ruby
# config/routes.rb
Rails.application.routes.draw do
  root 'chat#index'
  
  get 'chat/index'
  post 'chat', to: 'chat#create'
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the Rails server after updating the `.env` file. The `dotenv-rails` gem loads environment variables on boot. |
| Assistant ID Not Found | The API returns a 404 error or "Assistant not found" message. | Confirm that `TELNYX_ASSISTANT_ID` in your `.env` file is set to a valid assistant ID. Verify the assistant exists in the [Telnyx Portal](https://portal.telnyx.com) under AI Assistants. If you don't have an assistant yet, create one via the Portal or use the create assistant API endpoint. |
| Empty Messages Array Error | The endpoint returns `{"error": "Messages array required and must not be empty"}` with HTTP 400. | Ensure your POST request includes a `messages` parameter with at least one message object. Each message must have `role` (either "user" or "assistant") and `content` (the message text). Example: `{"messages": [{"role": "user", "content": "Hello"}]}`. |
| CSRF Token Mismatch | Browser console shows "Can't verify CSRF token authenticity" error. | The Rails CSRF protection is blocking the request. Ensure your JavaScript includes the CSRF token in the request headers: `'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content`. Verify the `<meta name="csrf-token">` tag is present in your layout file (`app/views/layouts/application.html.erb`). |
| Rate Limit Exceeded (429) | The API returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429. | You've exceeded the Telnyx API rate limit. Implement exponential backoff in your client-side JavaScript or add server-side request throttling. Wait a few seconds before retrying. Check your API usage in the [Telnyx Portal](https://portal.telnyx.com) to understand your rate limits. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this AI example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Ruby version do I need?**

Ruby 3.1 or higher. Ruby 3.3 is recommended.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [AI Assistants Guide](https://developers.telnyx.com/docs/inference/ai-assistants/no-code-voice-assistant)
- [Assistants API Reference](https://developers.telnyx.com/api-reference/assistants/create-an-assistant)
- [Ruby SDK](https://developers.telnyx.com/development/sdk/ruby)
- [Telnyx AI Assistants](https://telnyx.com/ai-assistants)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [List AI Assistants](/tutorials/ai/ruby/list-ai-assistants).
- [Create an AI Assistant](/tutorials/ai/ruby/create-ai-assistant).
- [Clone an AI Assistant](/tutorials/ai/ruby/clone-ai-assistant).
