# Inbound Call Webhook with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails application that receives and handles inbound call webhooks from the Telnyx Voice API. This tutorial demonstrates how to set up a webhook endpoint, validate incoming requests, extract call metadata, and respond to call events using the Telnyx Ruby SDK. You'll learn the command-event model that powers Telnyx Call Control and how to safely process webhook payloads in a Rails controller.

## Who Is This For?

- **Ruby developers** building voice features with Rails.
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

- Ruby 2.7 or higher.
- Rails 6.0 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound calls.
- A publicly accessible URL (ngrok, Heroku, or similar) to receive webhooks during development.
- Bundler (Ruby package manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/route-phone-calls-to-ai-agent-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/route-phone-calls-to-ai-agent-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Update your webhook controller to handle inbound call events. Edit `app/controllers/webhooks_controller.rb`:

```ruby
class WebhooksController < ApplicationController
  # Disable CSRF protection for webhook endpoints (Telnyx sends POST without token)
  skip_before_action :verify_authenticity_token, only: [:inbound_call]

  def inbound_call
    # Parse the incoming webhook payload
    event_data = request.raw_post
    event = JSON.parse(event_data)

    # Extract call metadata from the webhook
    call_control_id = event.dig('data', 'call_control_id')
    from_number = event.dig('data', 'from')
    to_number = event.dig('data', 'to')
    event_type = event.dig('data', 'event_type')

    # Log the incoming call for debugging and audit trails
    Rails.logger.info("Inbound call received: #{call_control_id} from #{from_number} to #{to_number}")

    # Handle different call events
    case event_type
    when 'call.initiated'
      handle_call_initiated(call_control_id, from_number, to_number)
    when 'call.answered'
      handle_call_answered(call_control_id)
    when 'call.hangup'
      handle_call_hangup(call_control_id)
    else
      Rails.logger.warn("Unhandled event type: #{event_type}")
    end

    # Always return 200 OK to acknowledge receipt of the webhook
    render json: { status: 'received' }, status: :ok
  rescue JSON::ParserError => e
    Rails.logger.error("Failed to parse webhook payload: #{e.message}")
    render json: { error: 'Invalid JSON' }, status: :bad_request
  rescue StandardError => e
    Rails.logger.error("Webhook processing error: #{e.message}")
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end

  private

  def handle_call_initiated(call_control_id, from_number, to_number)
    # Called when an inbound call arrives but before it's answered
    # Use this to route calls, check caller ID, or trigger business logic
    Rails.logger.info("Call initiated: #{call_control_id}")

    # Example: Answer the call automatically
    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.answer(call_control_id)
      Rails.logger.info("Call answered: #{call_control_id}")
    rescue Telnyx::AuthenticationError
      Rails.logger.error("Authentication failed: invalid API key")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error answering call: #{e.message}")
    rescue Telnyx::APIConnectionError
      Rails.logger.error("Network error connecting to Telnyx")
    end
  end

  def handle_call_answered(call_control_id)
    # Called when the call is successfully answered
    Rails.logger.info("Call answered: #{call_control_id}")

    # Example: Start recording the call
    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.start_recording(call_control_id)
      Rails.logger.info("Recording started: #{call_control_id}")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error starting recording: #{e.message}")
    end
  end

  def handle_call_hangup(call_control_id)
    # Called when the call ends
    Rails.logger.info("Call ended: #{call_control_id}")

    # Example: Stop recording and clean up resources
    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.stop_recording(call_control_id)
      Rails.logger.info("Recording stopped: #{call_control_id}")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error stopping recording: #{e.message}")
    end
  end
end
```

Configure your Rails routes to accept POST requests to the webhook endpoint. Edit `config/routes.rb`:

```ruby
Rails.application.routes.draw do
  post 'webhooks/inbound_call', to: 'webhooks#inbound_call'
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Webhook not received | Your Rails application does not receive webhook POST requests from Telnyx. | Verify that ngrok is running and the tunnel URL is correctly configured in the Telnyx Portal. Check that your webhook URL in the portal matches your ngrok URL exactly (e.g., `https://abc123.ngrok.io/webhooks/inbound_call`). Ensure your Rails server is running on port 3000 and ngrok is forwarding to that port. Check Rails logs for any errors. |
| Authentication Error (401) | The controller logs show "Authentication failed: invalid API key" when attempting to answer or record calls. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes in the `.env` file. Restart your Rails server after updating the `.env` file to reload environment variables. |
| CSRF token validation failed | Rails returns a 422 error when Telnyx sends the webhook POST request. | The `skip_before_action :verify_authenticity_token, only: [:inbound_call]` line in the controller disables CSRF protection for this endpoint. Verify this line is present in your `WebhooksController`. CSRF protection is disabled only for the webhook endpoint; other routes remain protected. |
| JSON parsing error | The controller logs show "Failed to parse webhook payload: unexpected token" or similar JSON errors. | Ensure you are using `request.raw_post` to read the raw request body, not `request.body` or `params`. The webhook payload is sent as raw JSON in the request body, not as form-encoded parameters. Verify your JSON parsing logic handles the nested structure correctly using `.dig()` for safe access. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this Voice example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Ruby version do I need?**

Ruby 3.1 or higher. Ruby 3.3 is recommended.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Voice API Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [AI Assistant Start](https://developers.telnyx.com/docs/voice/programmable-voice/ai-assistant-start)
- [Call Control API Reference](https://developers.telnyx.com/api-reference/call-commands/dial)
- [Ruby SDK](https://developers.telnyx.com/development/sdk/ruby)
- [Telnyx Voice API](https://telnyx.com/products/voice-api)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [Make an Outbound Call with Ruby](/tutorials/voice/ruby/outbound-call).
- [Record a Call with Ruby](/tutorials/voice/ruby/call-recording).
- [Transfer a Call with Ruby](/tutorials/voice/ruby/call-transfer).
