# SIP Trunking Setup with Ruby and Rails

## What Does This Example Do?

Build a production-ready Rails application that manages SIP trunk connections using the Telnyx Ruby SDK. This tutorial demonstrates how to create SIP connections, configure authentication, and integrate with your PBX or SBC. You'll learn the new client-based initialization pattern, proper error handling for telecom APIs, and secure credential management via environment variables.

## Who Is This For?

- **Ruby developers** building sip features with Rails.
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
- A SIP-capable PBX, SBC, or softphone (Asterisk, FreeSWITCH, 3CX, or similar).
- Bundler (Ruby dependency manager).
- A publicly accessible IP address or domain for your Rails application (for webhook callbacks).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-ruby
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-ruby
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle SIP connection logic in `app/services/sip_connection_service.rb`:

```ruby
# app/services/sip_connection_service.rb
class SipConnectionService
  def initialize(client = TELNYX_CLIENT)
    @client = client
  end

  def create_connection(name:, username:, password:, sip_endpoint:)
    """Create a new SIP connection with credential authentication."""
    # Validate required parameters
    raise ArgumentError, "Name is required" if name.blank?
    raise ArgumentError, "Username is required" if username.blank?
    raise ArgumentError, "Password is required" if password.blank?
    raise ArgumentError, "SIP endpoint is required" if sip_endpoint.blank?

    # Create the SIP connection via Telnyx API
    response = @client.sip_connections.create(
      connection_name: name,
      inbound: {
        sip_subdomain: name.downcase.gsub(/[^a-z0-9]/, ""),
      },
      outbound: {
        outbound_voice_profile_id: nil, # Optional: set if you have a profile
        sip_address: sip_endpoint,
      },
      credentials: {
        authentication: {
          authentication_type: "credential",
          username: username,
          password: password,
        }
      }
    )

    # Extract serializable data — SDK objects are NOT JSON-serializable
    {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.authentication&.username,
      sip_endpoint: response.data.outbound&.sip_address,
      status: response.data.active ? "active" : "inactive",
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def list_connections(limit: 10, after: nil)
    """Retrieve all SIP connections with pagination support."""
    params = { limit: limit }
    params[:after] = after if after.present?

    response = @client.sip_connections.list(**params)

    # Map response data to serializable hashes
    {
      connections: response.data.map do |conn|
        {
          id: conn.id,
          name: conn.connection_name,
          username: conn.credentials&.authentication&.username,
          sip_endpoint: conn.outbound&.sip_address,
          status: conn.active ? "active" : "inactive",
          created_at: conn.created_at,
        }
      end,
      pagination: {
        limit: response.meta&.pagination&.page_size,
        after: response.meta&.pagination&.after,
      }
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def get_connection(connection_id)
    """Retrieve a specific SIP connection by ID."""
    raise ArgumentError, "Connection ID is required" if connection_id.blank?

    response = @client.sip_connections.retrieve(connection_id)

    {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.authentication&.username,
      sip_endpoint: response.data.outbound&.sip_address,
      status: response.data.active ? "active" : "inactive",
      created_at: response.data.created_at,
      updated_at: response.data.updated_at,
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def delete_connection(connection_id)
    """Delete a SIP connection by ID."""
    raise ArgumentError, "Connection ID is required" if connection_id.blank?

    @client.sip_connections.delete(connection_id)
    { success: true, message: "SIP connection deleted successfully" }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end
end
```

Update your controller in `app/controllers/sip_connections_controller.rb`:

```ruby
# app/controllers/sip_connections_controller.rb
class SipConnectionsController < ApplicationController
  before_action :initialize_service

  # GET /sip_connections
  def index
    begin
      result = @service.list_connections(limit: params[:limit] || 10)
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

  # POST /sip_connections
  def create
    begin
      # Validate required parameters
      required_params = [:name, :username, :password, :sip_endpoint]
      missing_params = required_params.select { |p| params[p].blank? }
      
      if missing_params.any?
        return render json: { error: "Missing required fields: #{missing_params.join(', ')}" }, status: :bad_request
      end

      result = @service.create_connection(
        name: params[:name],
        username: params[:username],
        password: params[:password],
        sip_endpoint: params[:sip_endpoint]
      )
      render json: result, status: :created
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  # GET /sip_connections/:id
  def show
    begin
      result = @service.get_connection(params[:id])
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  # DELETE /sip_connections/:id
  def destroy
    begin
      result = @service.delete_connection(params[:id])
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  private

  def initialize_service
    @service = SipConnectionService.new
  end
end
```

Add routes to `config/routes.rb`:

```ruby
Rails.application.routes.draw do
  resources :sip_connections, only: [:index, :create, :show, :destroy]
end
```

## Complete Code

See [`app.rb`](./app.rb) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your environment file and restart the Rails server with `rails server`. |
| Missing Required Fields | You receive a 400 error stating "Missing required fields: name, username, password, sip_endpoint". | Ensure your POST request includes all four required parameters in the JSON body. Example: `{"name": "office-pbx", "username": "pbx_user", "password": "secure_password_123", "sip_endpoint": "192.0.2.1"}`. Verify the Content-Type header is set to `application/json`. |
| Network Error Connecting to Telnyx | The endpoint returns `{"error": "Network error connecting to Telnyx"}` with HTTP 503. | Check your internet connection and verify that your Rails application can reach `api.telnyx.com`. If behind a firewall or proxy, ensure outbound HTTPS (port 443) is allowed. Verify the Telnyx API is not experiencing an outage by checking the [Telnyx Status Page](https://status.telnyx.com). |
| SIP Connection Not Receiving Calls | The SIP connection is created successfully but your PBX is not receiving inbound calls. | Verify that your PBX's IP address in the `sip_endpoint` parameter is correct and publicly routable. Ensure your PBX is configured to accept SIP traffic on port 5060 (UDP) or 5061 (TLS). Check firewall rules to allow inbound SIP traffic from Telnyx's IP ranges. Test connectivity using a SIP client like Linphone or Zoiper. |
| Rate Limit Exceeded | The endpoint returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429. | The Telnyx API enforces rate limits. Implement exponential backoff in your application: wait 1 second, then 2 seconds, then 4 seconds between retries. Cache SIP connection data locally to reduce API calls. Contact Telnyx support if you need higher rate limits for your use case. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SIP example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Ruby version do I need?**

Ruby 3.1 or higher. Ruby 3.3 is recommended.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [SIP Trunking Get Started](https://developers.telnyx.com/docs/voice/sip-trunking/get-started)
- [SIP Configuration Guides](https://developers.telnyx.com/docs/voice/sip-trunking/configuration-guides)
- [Ruby SDK](https://developers.telnyx.com/development/sdk/ruby)
- [Telnyx SIP Trunks](https://telnyx.com/products/sip-trunks)
- [SIP Trunking Pricing](https://telnyx.com/pricing/elastic-sip)

## Related Examples

- [Configure SIP Authentication Methods](/tutorials/sip/ruby/sip-authentication).
- [Set Up Failover Routing for SIP Trunks](/tutorials/sip/ruby/failover-routing).
- [Handle Inbound SIP Routing with Webhooks](/tutorials/sip/ruby/inbound-sip-routing).
