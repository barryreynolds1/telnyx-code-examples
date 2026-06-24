#!/usr/bin/env ruby
"""Production-ready Sinatra app for SIP failover routing via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv"
require "json"

Dotenv.load

# Initialize Telnyx client with the new SDK pattern
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# In-memory store for endpoint health status (use Redis in production)
ENDPOINT_STATUS = {
  primary: { uri: ENV["PRIMARY_SIP_ENDPOINT"], healthy: true, last_check: Time.now },
  backup: { uri: ENV["BACKUP_SIP_ENDPOINT"], healthy: true, last_check: Time.now }
}

# Helper function to create or update a SIP connection
def create_sip_connection(client, name, username, password, sip_uri)
  """Create a SIP connection with credential authentication."""
  begin
    response = client.sip_connections.create(
      connection_name: name,
      outbound_voice_profile_id: nil,
      inbound: {
        sip_subdomain: "#{name.downcase.gsub(/\s+/, '-')}"
      },
      credentials: [
        {
          username: username,
          password: password
        }
      ]
    )
    
    return {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.first&.username
    }
  rescue Telnyx::AuthenticationError => e
    raise "Authentication failed: #{e.message}"
  rescue Telnyx::APIStatusError => e
    raise "API error (#{e.status_code}): #{e.message}"
  end
end

# Helper function to list all SIP connections
def list_sip_connections(client)
  """Retrieve all SIP connections for the account."""
  begin
    response = client.sip_connections.list
    
    response.data.map do |conn|
      {
        id: conn.id,
        name: conn.connection_name,
        username: conn.credentials&.first&.username,
        inbound_subdomain: conn.inbound&.sip_subdomain
      }
    end
  rescue Telnyx::APIStatusError => e
    raise "Failed to list connections: #{e.message}"
  end
end

# Helper function to retrieve a specific SIP connection
def get_sip_connection(client, connection_id)
  """Fetch details of a specific SIP connection."""
  begin
    response = client.sip_connections.retrieve(connection_id)
    
    {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.first&.username,
      inbound_subdomain: response.data.inbound&.sip_subdomain
    }
  rescue Telnyx::APIStatusError => e
    raise "Connection not found: #{e.message}"
  end
end

# Helper function to assign phone number to SIP connection
def assign_phone_to_connection(client, phone_number, connection_id)
  """Assign a Telnyx phone number to a SIP connection."""
  begin
    response = client.phone_numbers.update(
      phone_number,
      connection_id: connection_id
    )
    
    {
      phone_number: response.data.phone_number,
      connection_id: response.data.connection_id
    }
  rescue Telnyx::APIStatusError => e
    raise "Failed to assign phone number: #{e.message}"
  end
end

# Helper function to determine the active endpoint based on health
def get_active_endpoint
  """Return the URI of the healthy endpoint, with failover logic."""
  if ENDPOINT_STATUS[:primary][:healthy]
    ENDPOINT_STATUS[:primary][:uri]
  elsif ENDPOINT_STATUS[:backup][:healthy]
    ENDPOINT_STATUS[:backup][:uri]
  else
    ENDPOINT_STATUS[:primary][:uri]
  end
end

# Helper function to mark endpoint as unhealthy
def mark_endpoint_unhealthy(endpoint_key)
  """Mark an endpoint as unhealthy after a failed call attempt."""
  ENDPOINT_STATUS[endpoint_key][:healthy] = false
  ENDPOINT_STATUS[endpoint_key][:last_check] = Time.now
end

# Helper function to mark endpoint as healthy
def mark_endpoint_healthy(endpoint_key)
  """Mark an endpoint as healthy after successful call."""
  ENDPOINT_STATUS[endpoint_key][:healthy] = true
  ENDPOINT_STATUS[endpoint_key][:last_check] = Time.now
end

# Sinatra error handler for Telnyx exceptions
error Telnyx::AuthenticationError do
  status 401
  json({ error: "Invalid API key" })
end

error Telnyx::RateLimitError do
  status 429
  json({ error: "Rate limit exceeded. Please slow down." })
end

error Telnyx::APIStatusError do |e|
  status e.status_code || 500
  json({ error: e.message, status_code: e.status_code })
end

error Telnyx::APIConnectionError do
  status 503
  json({ error: "Network error connecting to Telnyx" })
end

# Route: Create a new SIP connection
post "/sip/connections" do
  request.body.rewind
  data = JSON.parse(request.body.read)
  
  unless data["name"] && data["username"] && data["password"] && data["sip_uri"]
    return status 400, json({ error: "Missing required fields: name, username, password, sip_uri" })
  end
  
  begin
    result = create_sip_connection(
      client,
      data["name"],
      data["username"],
      data["password"],
      data["sip_uri"]
    )
    status 201
    json(result)
  rescue => e
    status 400
    json({ error: e.message })
  end
end

# Route: List all SIP connections
get "/sip/connections" do
  begin
    connections = list_sip_connections(client)
    json(connections)
  rescue => e
    status 500
    json({ error: e.message })
  end
end

# Route: Get a specific SIP connection
get "/sip/connections/:id" do
  begin
    connection = get_sip_connection(client, params[:id])
    json(connection)
  rescue => e
    status 404
    json({ error: e.message })
  end
end

# Route: Assign phone number to SIP connection
post "/sip/phone-assignments" do
  request.body.rewind
  data = JSON.parse(request.body.read)
  
  unless data["phone_number"] && data["connection_id"]
    return status 400, json({ error: "Missing required fields: phone_number, connection_id" })
  end
  
  begin
    result = assign_phone_to_connection(client, data["phone_number"], data["connection_id"])
    json(result)
  rescue => e
    status 400
    json({ error: e.message })
  end
end

# Route: Get current failover status
get "/sip/failover-status" do
  status_info = {
    primary: {
      uri: ENDPOINT_STATUS[:primary][:uri],
      healthy: ENDPOINT_STATUS[:primary][:healthy],
      last_check: ENDPOINT_STATUS[:primary][:last_check]
    },
    backup: {
      uri: ENDPOINT_STATUS[:backup][:uri],
      healthy: ENDPOINT_STATUS[:backup][:healthy],
      last_check: ENDPOINT_STATUS[:backup][:last_check]
    },
    active_endpoint: get_active_endpoint
  }
  
  json(status_info)
end

# Route: Webhook to receive inbound call events
post "/webhooks/call" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  event_type = payload["data"]["event_type"]
  call_id = payload["data"]["call_id"]
  
  case event_type
  when "call.initiated"
    active_endpoint = get_active_endpoint
    puts "Inbound call #{call_id} routing to: #{active_endpoint}"
    
    status 200
    json({ status: "call_routed", endpoint: active_endpoint })
    
  when "call.answered"
    mark_endpoint_healthy(:primary)
    puts "Call #{call_id} answered successfully"
    
    status 200
    json({ status: "acknowledged" })
    
  when "call.failed"
    failure_reason = payload["data"]["failure_reason"]
    puts "Call #{call_id} failed: #{failure_reason}"
    
    if ENDPOINT_STATUS[:primary][:healthy]
      mark_endpoint_unhealthy(:primary)
      puts "Primary endpoint marked unhealthy. Failover to backup."
    end
    
    status 200
    json({ status: "failover_triggered" })
    
  else
    status 200
    json({ status: "event_received" })
  end
end

# Route: Health check endpoint for monitoring
get "/health" do
  json({
    status: "healthy",
    timestamp: Time.now.iso8601,
    endpoints: {
      primary: ENDPOINT_STATUS[:primary][:healthy] ? "up" : "down",
      backup: ENDPOINT_STATUS[:backup][:healthy] ? "up" : "down"
    }
  })
end

# Root route
get "/" do
  json({
    service: "Telnyx SIP Failover Routing",
    version: "1.0.0",
    endpoints: {
      "POST /sip/connections": "Create a new SIP connection",
      "GET /sip/connections": "List all SIP connections",
      "GET /sip/connections/:id": "Get a specific SIP connection",
      "POST /sip/phone-assignments": "Assign phone number to connection",
      "GET /sip/failover-status": "Get current failover status",
      "POST /webhooks/call": "Receive inbound call events",
      "GET /health": "Health check endpoint"
    }
  })
end
