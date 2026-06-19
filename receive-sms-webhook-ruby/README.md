# Receive SMS Webhook with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails webhook endpoint that receives inbound SMS messages from Telnyx. This tutorial demonstrates how to configure a Messaging Profile with a webhook URL, handle inbound SMS events, and persist message data using Rails models. You'll learn the new Telnyx Ruby SDK initialization pattern, proper error handling for telecom webhooks, and secure credential management via environment variables.

## Who Is This For?

- **Ruby developers** building sms features with Rails.
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
- A Telnyx phone number enabled for inbound SMS.
- A publicly accessible URL (ngrok, Heroku, or similar) to receive webhooks during development.
- Bundler (Ruby package manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a Rails controller to handle incoming webhook events:

```bash
rails generate controller Webhooks sms
```

Edit `app/controllers/webhooks_controller.rb` to process inbound SMS:

```ruby
class WebhooksController < ApplicationController
  # Disable CSRF protection for webhook endpoint (Telnyx sends unsigned requests)
  skip_before_action :verify_authenticity_token, only: [:sms]

  def sms
    # Parse the incoming webhook payload
    event_type = params.dig(:data, :event_type)
    
    # Only process message.received events
    if event_type == 'message.received'
      process_inbound_message
      render json: { success: true }, status: :ok
    else
      render json: { success: false, error: 'Unsupported event type' }, status: :unprocessable_entity
    end
  rescue StandardError => e
    # Log the error and return 500 to signal Telnyx to retry
    Rails.logger.error("Webhook processing error: #{e.message}")
    render json: { error: e.message }, status: :internal_server_error
  end

  private

  def process_inbound_message
    # Extract message data from webhook payload
    message_data = params.dig(:data, :payload)
    return unless message_data

    from_number = message_data.dig(:from, :phone_number)
    to_number = message_data.dig(:to, 0, :phone_number)
    message_id = message_data[:id]
    text = message_data[:text]
    received_at = message_data[:received_at]

    # Validate required fields
    raise ArgumentError, 'Missing required fields' unless from_number && to_number && message_id

    # Store the inbound message in the database
    InboundMessage.create!(
      message_id: message_id,
      from_number: from_number,
      to_number: to_number,
      text: text,
      received_at: received_at
    )

    Rails.logger.info("Inbound SMS received from #{from_number}: #{text}")
  end
end
```

Update your `config/routes.rb` to add the webhook route:

```ruby
Rails.application.routes.draw do
  post 'webhooks/sms', to: 'webhooks#sms'
end
```

Create a service to configure the Messaging Profile webhook (optional but recommended):

```bash
rails generate service messaging_profile_service
```

Edit `app/services/messaging_profile_service.rb`:

```ruby
class MessagingProfileService
  def self.update_webhook_url(webhook_url)
    # Retrieve the default Messaging Profile
    profiles = Telnyx::MessagingProfile.list
    profile = profiles.data.first

    return { error: 'No Messaging Profile found' } unless profile

    # Update the webhook URL for inbound messages
    profile.webhook_url = webhook_url
    profile.webhook_api_version = '2'
    profile.save

    { success: true, profile_id: profile.id }
  rescue Telnyx::AuthenticationError
    { error: 'Invalid API key' }
  rescue Telnyx::APIStatusError => e
    { error: "API error: #{e.message}", status_code: e.status_code }
  rescue Telnyx::APIConnectionError
    { error: 'Network error connecting to Telnyx' }
  end
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Webhook not being triggered | You send an SMS to your Telnyx number but the webhook endpoint is never called. | Verify the webhook URL is publicly accessible by visiting it in your browser (you should see a Rails error page, not a connection timeout). Confirm the webhook URL is correctly configured in your Messaging Profile in the Telnyx Portal. If using ngrok, ensure the tunnel is still active and the URL hasn't changed. Check Rails logs for any errors: `tail -f log/development.log`. |
| Authentication Error (401) | The Telnyx SDK raises `Telnyx::AuthenticationError` when initializing or calling API methods. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart your Rails server after updating the `.env` file. Run `rails credentials:edit` if using Rails encrypted credentials instead of `.env`. |
| Messages not being saved to database | The webhook is received (HTTP 200 response) but no records appear in the `InboundMessage` table. | Check that the database migration ran successfully: `rails db:migrate`. Verify the webhook payload structure matches your code expectations by logging the raw params: add `Rails.logger.info(params.inspect)` at the start of the `sms` action. Ensure the `message_id` field is unique and not duplicated from previous test runs. |
| CSRF token validation error | The webhook returns a 422 Unprocessable Entity error mentioning CSRF token. | The `skip_before_action :verify_authenticity_token, only: [:sms]` line must be present in your `WebhooksController`. Verify the controller file is saved and the Rails server was restarted after adding this line. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SMS example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Ruby version do I need?**

Ruby 3.1 or higher. Ruby 3.3 is recommended.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Messaging Overview](https://developers.telnyx.com/docs/messaging)
- [Send an SMS — Quickstart](https://developers.telnyx.com/docs/messaging/messages/send-message)
- [Messaging API Reference](https://developers.telnyx.com/api-reference/messages/send-a-message)
- [Ruby SDK](https://developers.telnyx.com/development/sdk/ruby)
- [Telnyx SMS API](https://telnyx.com/products/sms-api)
- [Messaging Pricing](https://telnyx.com/pricing/messaging)

## Related Examples

- [Send a Single SMS with Ruby and Rails](/tutorials/sms/ruby/send-single-sms).
- [Build Two-Way SMS Conversations with Ruby and Rails](/tutorials/sms/ruby/two-way-sms).
- [Implement OTP and Two-Factor Authentication with Ruby and Rails](/tutorials/sms/ruby/otp-2fa).
