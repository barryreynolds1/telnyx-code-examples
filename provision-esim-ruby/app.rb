#!/usr/bin/env ruby
"""Production-ready Sinatra application for eSIM provisioning via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
def get_client
  Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
end

# Helper function to provision an eSIM profile
def provision_esim(device_id, carrier_code)
  """
  Provision an eSIM profile for a device.
  Returns JSON-serializable response data.
  """
  client = get_client
  
  # Validate inputs
  raise ArgumentError, "Device ID cannot be empty" if device_id.nil? || device_id.empty?
  raise ArgumentError, "Carrier code must be provided" if carrier_code.nil? || carrier_code.empty?
  
  # Call the eSIM provisioning API
  response = client.esim_profiles.create(
    device_identifier: device_id,
    carrier_code: carrier_code,
    callback_url: ENV["WEBHOOK_URL"]
  )
  
  # Extract serializable data — SDK objects are NOT JSON-serializable
  {
    profile_id: response.data.id,
    device_id: response.data.device_identifier,
    status: response.data.status,
    carrier_code: response.data.carrier_code,
    activation_code: response.data.activation_code,
    created_at: response.data.created_at
  }
rescue ArgumentError => e
  raise e
end

# Helper function to activate a provisioned eSIM profile
def activate_esim(profile_id, confirmation_code = nil)
  """
  Activate a provisioned eSIM profile.
  Returns JSON-serializable response data.
  """
  client = get_client
  
  raise ArgumentError, "Profile ID cannot be empty" if profile_id.nil? || profile_id.empty?
  
  # Activate the eSIM profile
  response = client.esim_profiles.activate(
    id: profile_id,
    confirmation_code: confirmation_code
  )
  
  {
    profile_id: response.data.id,
    status: response.data.status,
    activated_at: response.data.activated_at,
    device_id: response.data.device_identifier
  }
rescue ArgumentError => e
  raise e
end

# Helper function to retrieve eSIM profile status
def get_esim_status(profile_id)
  """
  Retrieve the current status of an eSIM profile.
  Returns JSON-serializable response data.
  """
  client = get_client
  
  raise ArgumentError, "Profile ID cannot be empty" if profile_id.nil? || profile_id.empty?
  
  response = client.esim_profiles.retrieve(profile_id)
  
  {
    profile_id: response.data.id,
    device_id: response.data.device_identifier,
    status: response.data.status,
    carrier_code: response.data.carrier_code,
    created_at: response.data.created_at,
    activated_at: response.data.activated_at
  }
rescue ArgumentError => e
  raise e
end

# Configure Sinatra
set :port, 4567
set :bind, "0.0.0.0"

# Route to provision a new eSIM profile
post "/esim/provision" do
  content_type :json
  
  # Parse request body
  begin
    data = JSON.parse(request.body.read)
  rescue JSON::ParserError
    return [400, { error: "Invalid JSON in request body" }.to_json]
  end
  
  device_id = data["device_id"]
  carrier_code = data["carrier_code"]
  
  # Validate required fields
  if !device_id || !carrier_code
    return [400, { error: "Missing required fields: 'device_id' and 'carrier_code'" }.to_json]
  end
  
  begin
    result = provision_esim(device_id, carrier_code)
    [201, result.to_json]
    
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

# Route to activate a provisioned eSIM profile
post "/esim/activate" do
  content_type :json
  
  begin
    data = JSON.parse(request.body.read)
  rescue JSON::ParserError
    return [400, { error: "Invalid JSON in request body" }.to_json]
  end
  
  profile_id = data["profile_id"]
  confirmation_code = data["confirmation_code"]
  
  if !profile_id
    return [400, { error: "Missing required field: 'profile_id'" }.to_json]
  end
  
  begin
    result = activate_esim(profile_id, confirmation_code)
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

# Route to retrieve eSIM profile status
get "/esim/status/:profile_id" do
  content_type :json
  
  profile_id = params["profile_id"]
  
  begin
    result = get_esim_status(profile_id)
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

# Webhook endpoint to receive eSIM status updates from Telnyx
post "/webhooks/esim" do
  content_type :json
  
  begin
    payload = JSON.parse(request.body.read)
  rescue JSON::ParserError
    return [400, { error: "Invalid JSON in webhook payload" }.to_json]
  end
  
  # Log the webhook event for debugging
  event_type = payload["event_type"]
  profile_id = payload["data"]["profile_id"]
  status = payload["data"]["status"]
  
  puts "[#{Time.now}] eSIM Webhook: #{event_type} - Profile #{profile_id} - Status: #{status}"
  
  # Process the webhook event based on type
  case event_type
  when "esim.profile.provisioned"
    # Handle provisioning completion
    puts "eSIM profile #{profile_id} provisioned successfully"
  when "esim.profile.activated"
    # Handle activation completion
    puts "eSIM profile #{profile_id} activated successfully"
  when "esim.profile.failed"
    # Handle provisioning/activation failure
    puts "eSIM profile #{profile_id} failed: #{payload['data']['error_message']}"
  else
    puts "Unknown eSIM event type: #{event_type}"
  end
  
  # Always return 200 to acknowledge receipt
  [200, { status: "received" }.to_json]
end

# Health check endpoint
get "/health" do
  content_type :json
  [200, { status: "ok" }.to_json]
end
