#!/usr/bin/env ruby
"""Production-ready Sinatra application for SIP connection registration via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# Helper function to create a SIP connection with credential authentication
def create_sip_connection(client, name, username, password, endpoint_ip)
  """Create a SIP connection for credential-based registration."""
  response = client.sip_connections.create(
    name: name,
    outbound_voice_profile_id: nil,
    inbound_addresses: [endpoint_ip],
    outbound_addresses: [endpoint_ip],
    credentials: [
      {
        username: username,
        password: password
      }
    ]
  )
  
  # Extract serializable data — SDK objects are NOT JSON-serializable
  {
    id: response.data.id,
    name: response.data.name,
    username: response.data.credentials&.first&.username,
    inbound_addresses: response.data.inbound_addresses,
    outbound_addresses: response.data.outbound_addresses,
    created_at: response.data.created_at
  }
end

# Helper function to list all SIP connections
def list_sip_connections(client)
  """Retrieve all SIP connections for the account."""
  response = client.sip_connections.list
  
  # Map SDK objects to plain hashes for JSON serialization
  response.data.map do |connection|
    {
      id: connection.id,
      name: connection.name,
      username: connection.credentials&.first&.username,
      inbound_addresses: connection.inbound_addresses,
      outbound_addresses: connection.outbound_addresses,
      created_at: connection.created_at
    }
  end
end

# Helper function to retrieve a specific SIP connection
def get_sip_connection(client, connection_id)
  """Fetch details of a single SIP connection."""
  response = client.sip_connections.retrieve(connection_id)
  
  {
    id: response.data.id,
    name: response.data.name,
    username: response.data.credentials&.first&.username,
    inbound_addresses: response.data.inbound_addresses,
    outbound_addresses: response.data.outbound_addresses,
    created_at: response.data.created_at
  }
end

# Sinatra route to create a new SIP connection
post "/sip/connections" do
  content_type :json
  
  data = JSON.parse(request.body.read)
  
  # Validate required fields
  unless data["name"] && data["username"] && data["password"] && data["endpoint_ip"]
    return [400, { error: "Missing required fields: name, username, password, endpoint_ip" }.to_json]
  end
  
  begin
    result = create_sip_connection(
      client,
      data["name"],
      data["username"],
      data["password"],
      data["endpoint_ip"]
    )
    [201, result.to_json]
    
  rescue Telnyx::AuthenticationError
    [401, { error: "Invalid API key" }.to_json]
  rescue Telnyx::RateLimitError
    [429, { error: "Rate limit exceeded. Please slow down." }.to_json]
  rescue Telnyx::APIStatusError => e
    [e.status_code, { error: e.message, status_code: e.status_code }.to_json]
  rescue Telnyx::APIConnectionError
    [503, { error: "Network error connecting to Telnyx" }.to_json]
  rescue StandardError => e
    [400, { error: e.message }.to_json]
  end
end

# Sinatra route to list all SIP connections
get "/sip/connections" do
  content_type :json
  
  begin
    result = list_sip_connections(client)
    [200, result.to_json]
    
  rescue Telnyx::AuthenticationError
    [401, { error: "Invalid API key" }.to_json]
  rescue Telnyx::RateLimitError
    [429, { error: "Rate limit exceeded. Please slow down." }.to_json]
  rescue Telnyx::APIStatusError => e
    [e.status_code, { error: e.message, status_code: e.status_code }.to_json]
  rescue Telnyx::APIConnectionError
    [503, { error: "Network error connecting to Telnyx" }.to_json]
  rescue StandardError => e
    [400, { error: e.message }.to_json]
  end
end

# Sinatra route to retrieve a specific SIP connection
get "/sip/connections/:id" do
  content_type :json
  
  connection_id = params["id"]
  
  begin
    result = get_sip_connection(client, connection_id)
    [200, result.to_json]
    
  rescue Telnyx::AuthenticationError
    [401, { error: "Invalid API key" }.to_json]
  rescue Telnyx::RateLimitError
    [429, { error: "Rate limit exceeded. Please slow down." }.to_json]
  rescue Telnyx::APIStatusError => e
    [e.status_code, { error: e.message, status_code: e.status_code }.to_json]
  rescue Telnyx::APIConnectionError
    [503, { error: "Network error connecting to Telnyx" }.to_json]
  rescue StandardError => e
    [400, { error: e.message }.to_json]
  end
end
