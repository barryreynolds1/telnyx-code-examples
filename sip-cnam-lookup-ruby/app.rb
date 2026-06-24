#!/usr/bin/env ruby
"""Production-ready Sinatra endpoint for CNAM lookups via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# Configure Sinatra
set :port, 5000
set :bind, "127.0.0.1"

def perform_cnam_lookup(phone_number)
  """Perform CNAM lookup and return JSON-serializable response data."""
  
  # Validate E.164 format to prevent API errors
  unless phone_number.start_with?("+")
    raise ArgumentError, "Phone number must be in E.164 format (e.g., +15551234567)"
  end
  
  # Remove the leading + for the API call (CNAM endpoint expects number without +)
  lookup_number = phone_number.delete_prefix("+")
  
  # Call Telnyx CNAM lookup endpoint
  response = client.cnam_lookups.retrieve(lookup_number)
  
  # Extract serializable data — SDK objects are NOT JSON-serializable
  {
    phone_number: phone_number,
    caller_name: response.data.caller_name,
    carrier_name: response.data.carrier_name,
    lookup_status: response.data.lookup_status,
  }
end

# Error handler for Telnyx authentication errors
error Telnyx::AuthenticationError do
  status 401
  json({ error: "Invalid API key" })
end

# Error handler for rate limiting
error Telnyx::RateLimitError do
  status 429
  json({ error: "Rate limit exceeded. Please slow down." })
end

# Error handler for API status errors
error Telnyx::APIStatusError do |e|
  status e.status_code || 500
  json({ error: e.message, status_code: e.status_code })
end

# Error handler for connection errors
error Telnyx::APIConnectionError do
  status 503
  json({ error: "Network error connecting to Telnyx" })
end

# Error handler for validation errors
error ArgumentError do |e|
  status 400
  json({ error: e.message })
end

# CNAM lookup endpoint
post "/cnam/lookup" do
  content_type :json
  
  # Parse request body
  begin
    data = JSON.parse(request.body.read)
  rescue JSON::ParserError
    return status(400) && json({ error: "Invalid JSON in request body" })
  end
  
  phone_number = data["phone_number"]
  
  unless phone_number
    return status(400) && json({ error: "Missing required field: 'phone_number'" })
  end
  
  # Perform lookup and return result
  result = perform_cnam_lookup(phone_number)
  json(result)
end

# Health check endpoint
get "/health" do
  content_type :json
  json({ status: "ok" })
end
