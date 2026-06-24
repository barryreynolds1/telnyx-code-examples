#!/usr/bin/env ruby
"""Production-ready Sinatra endpoint for number lookup via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize client with the new SDK pattern
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

def lookup_number(phone_number)
  """Perform number lookup via Telnyx and return JSON-serializable response data."""
  # Validate E.164 format to prevent API errors
  unless phone_number.start_with?("+")
    raise ArgumentError, "Phone number must be in E.164 format (e.g., +15551234567)"
  end

  # Use client.number_lookup.retrieve() to fetch carrier and line type details
  response = client.number_lookup.retrieve(phone_number)

  # Extract serializable data — SDK objects are NOT JSON-serializable
  {
    phone_number: response.data.phone_number,
    carrier_name: response.data.carrier_name,
    line_type: response.data.line_type,
    line_type_details: response.data.line_type_details,
    country_code: response.data.country_code,
    number_type: response.data.number_type,
    portability_status: response.data.portability_status,
  }
end

set :port, 5000
set :bind, "0.0.0.0"

# Health check endpoint
get "/" do
  content_type :json
  { status: "ok" }.to_json
end

# Number lookup endpoint
post "/lookup" do
  content_type :json

  # Parse request body
  begin
    data = JSON.parse(request.body.read)
  rescue JSON::ParserError
    return [400, { error: "Invalid JSON in request body" }.to_json]
  end

  phone_number = data["phone_number"]

  unless phone_number
    return [400, { error: "Missing required field: 'phone_number'" }.to_json]
  end

  begin
    result = lookup_number(phone_number)
    [200, result.to_json]

  rescue Telnyx::AuthenticationError
    [401, { error: "Invalid API key" }.to_json]
  rescue Telnyx::RateLimitError
    [429, { error: "Rate limit exceeded. Please slow down." }.to_json]
  rescue Telnyx::APIStatusError => e
    [e.status_code, { error: e.message, status_code: e.status_code }.to_json]
  rescue Telnyx::APIConnectionError
    [503, { error: "Network error connecting to Telnyx" }.to_json]
  rescue ArgumentError => e
    [400, { error: e.message }.to_json]
  end
end
