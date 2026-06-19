# SIM Activation with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails application that activates SIM cards using the Telnyx IoT SDK. This tutorial demonstrates the new client-based initialization pattern, proper error handling for IoT operations, and secure credential management via environment variables. You'll create a REST endpoint that activates a SIM card and returns its updated status.

## Who Is This For?

- **Ruby developers** building iot features with Rails.
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
- At least one SIM card in your Telnyx account (in `ready` or `inactive` status).
- Bundler (Ruby package manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a helper module in `app/helpers/telnyx_helper.rb` to initialize the Telnyx client:

```ruby
module TelnyxHelper
  def self.client
    @client ||= Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
  end
end
```

Update `app/controllers/sim_cards_controller.rb` with the activation logic and comprehensive error handling:

```ruby
class SimCardsController < ApplicationController
  rescue_from Telnyx::AuthenticationError, with: :handle_authentication_error
  rescue_from Telnyx::RateLimitError, with: :handle_rate_limit_error
  rescue_from Telnyx::APIStatusError, with: :handle_api_status_error
  rescue_from Telnyx::APIConnectionError, with: :handle_connection_error

  def activate
    sim_card_id = params[:id]

    if sim_card_id.blank?
      return render json: { error: "SIM card ID is required" }, status: :bad_request
    end

    # Call the Telnyx API to activate the SIM card
    response = TelnyxHelper.client.sim_cards.activate(sim_card_id)

    # Extract serializable data — SDK objects are NOT JSON-serializable
    sim_data = {
      id: response.data.id,
      iccid: response.data.iccid,
      status: response.data.status,
      sim_card_group_id: response.data.sim_card_group_id,
      phone_number: response.data.phone_number,
    }

    render json: sim_data, status: :ok
  end

  private

  def handle_authentication_error
    render json: { error: "Invalid API key" }, status: :unauthorized
  end

  def handle_rate_limit_error
    render json: { error: "Rate limit exceeded. Please slow down." }, status: :too_many_requests
  end

  def handle_api_status_error(exception)
    render json: { error: exception.message, status_code: exception.status_code }, status: exception.status_code
  end

  def handle_connection_error
    render json: { error: "Network error connecting to Telnyx" }, status: :service_unavailable
  end
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your environment file and restart the Rails server with `rails server`. |
| SIM Card Not Found (404) | You receive a 404 error stating "SIM card not found" when attempting to activate. | Confirm the SIM card ID is correct and exists in your Telnyx account. Log in to the [Telnyx Portal](https://portal.telnyx.com), navigate to IoT → SIM Cards, and copy the exact ID of the SIM card you want to activate. Verify the SIM card status is `ready` or `inactive` before attempting activation. |
| Environment Variable Not Set | The application raises an error about missing `TELNYX_API_KEY` on the first request. | Confirm your `.env` file exists in the Rails root directory and contains the variable. Ensure the file is named exactly `.env` (not `.env.txt` or `env`). The `dotenv-rails` gem must be in your `Gemfile`. Restart the Rails server after creating or modifying the `.env` file. |
| Rate Limit Error (429) | The endpoint returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429. | You have exceeded the Telnyx API rate limit. Wait a few seconds before making additional requests. For production applications, implement exponential backoff retry logic in your controller or a background job queue. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this IoT example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Ruby version do I need?**

Ruby 3.1 or higher. Ruby 3.3 is recommended.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [IoT SIM Get Started](https://developers.telnyx.com/docs/iot-sim/get-started)
- [SIM Card API Reference](https://developers.telnyx.com/api-reference/sim-cards/get-all-sim-cards)
- [Ruby SDK](https://developers.telnyx.com/development/sdk/ruby)
- [Telnyx IoT SIM Cards](https://telnyx.com/products/iot-sim-card)
- [IoT Data Plans Pricing](https://telnyx.com/pricing/iot-data-plans)

## Related Examples

- [Monitor SIM Card Data Usage](/tutorials/iot/ruby/data-usage-monitoring).
- [Configure Custom APN Settings](/tutorials/iot/ruby/apn-configuration).
- [Handle SIM Status Change Webhooks](/tutorials/iot/ruby/sim-status-webhook).
