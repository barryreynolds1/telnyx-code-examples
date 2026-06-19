# Outbound Call with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails endpoint that initiates outbound calls using the Telnyx Ruby SDK. This tutorial demonstrates the client-based initialization pattern, proper error handling for telecom APIs, secure credential management via environment variables, and Rails-idiomatic patterns for handling call control responses.

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
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application ID (connection_id) configured in the Telnyx Portal.
- Bundler (Ruby dependency manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle call initiation logic in `app/services/call_service.rb`:

```ruby
# app/services/call_service.rb
class CallService
  def self.initiate_call(to_number:)
    from_number = ENV["TELNYX_PHONE_NUMBER"]
    connection_id = ENV["TELNYX_CONNECTION_ID"]
    
    # Validate required environment variables
    raise "TELNYX_PHONE_NUMBER not configured" unless from_number
    raise "TELNYX_CONNECTION_ID not configured" unless connection_id
    
    # Validate E.164 format to prevent API errors
    raise "Phone number must be in E.164 format (e.g., +15551234567)" unless to_number.start_with?("+")
    
    # Initiate the call using the Telnyx SDK
    response = TELNYX_CLIENT.calls.dial(
      from_: from_number,
      to: to_number,
      connection_id: connection_id
    )
    
    # Extract serializable data — SDK objects are NOT JSON-serializable
    {
      call_control_id: response.data.call_control_id,
      from: from_number,
      to: to_number,
      state: response.data.state
    }
  end
end
```

Update the controller in `app/controllers/calls_controller.rb` with comprehensive error handling:

```ruby
# app/controllers/calls_controller.rb
class CallsController < ApplicationController
  def initiate
    # Parse JSON request body
    body = JSON.parse(request.body.read)
    to_number = body["to"]
    
    # Validate required parameters
    return render json: { error: "Missing required field: 'to'" }, status: :bad_request unless to_number
    
    # Call the service to initiate the call
    result = CallService.initiate_call(to_number: to_number)
    render json: result, status: :ok
    
  rescue Telnyx::AuthenticationError
    render json: { error: "Invalid API key" }, status: :unauthorized
  rescue Telnyx::RateLimitError
    render json: { error: "Rate limit exceeded. Please slow down." }, status: :too_many_requests
  rescue Telnyx::APIStatusError => e
    render json: { error: e.message, status_code: e.status_code }, status: e.status_code
  rescue Telnyx::APIConnectionError
    render json: { error: "Network error connecting to Telnyx" }, status: :service_unavailable
  rescue StandardError => e
    render json: { error: e.message }, status: :bad_request
  end
end
```

Configure the route in `config/routes.rb`:

```ruby
# config/routes.rb
Rails.application.routes.draw do
  post "/calls/initiate", to: "calls#initiate"
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your environment file and restart the Rails server with `rails server`. |
| Invalid Phone Number Format | You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination. | Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers. |
| Connection ID Not Configured | The application raises an error "TELNYX_CONNECTION_ID not configured" when initiating a call. | Verify your `.env` file contains the `TELNYX_CONNECTION_ID` variable with your Call Control Application ID from the Telnyx Portal. Ensure the file is named exactly `.env` (not `.env.txt`). Restart the Rails server after updating the environment file. |

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

- [Receive Inbound Call Webhooks with Ruby](/tutorials/voice/ruby/inbound-call-webhook).
- [Record Calls with Ruby](/tutorials/voice/ruby/call-recording).
- [Transfer Calls with Ruby](/tutorials/voice/ruby/call-transfer).
