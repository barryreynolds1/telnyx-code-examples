#!/usr/bin/env ruby
"""Production-ready Sinatra endpoint for cloning AI Assistants via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
def get_client
  Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
end

def clone_assistant(source_assistant_id, new_name)
  """Clone an AI Assistant and return JSON-serializable response data."""
  client = get_client
  
  # Retrieve the source assistant to validate it exists
  source_response = client.ai_assistants.retrieve(source_assistant_id)
  source = source_response.data
  
  if source.nil?
    raise "Source assistant not found"
  end
  
  # Use the clone endpoint to duplicate the assistant
  # The clone method handles copying all configuration including model, instructions, and tools
  clone_response = client.ai_assistants.clone(
    source_assistant_id,
    name: new_name
  )
  
  # Extract serializable data — SDK objects are NOT JSON-serializable
  {
    id: clone_response.data.id,
    name: clone_response.data.name,
    model: clone_response.data.model,
    instructions: clone_response.data.instructions,
    enabled_features: clone_response.data.enabled_features,
    created_at: clone_response.data.created_at
  }
end

post "/assistants/clone" do
  # Set response content type to JSON
  content_type :json
  
  # Parse incoming JSON request body
  request_body = JSON.parse(request.body.read)
  
  source_assistant_id = request_body["source_assistant_id"]
  new_name = request_body["new_name"]
  
  # Validate required fields
  if !source_assistant_id || !new_name
    status 400
    return { error: "Missing required fields: 'source_assistant_id' and 'new_name'" }.to_json
  end
  
  begin
    result = clone_assistant(source_assistant_id, new_name)
    status 201
    return result.to_json
    
  rescue Telnyx::AuthenticationError
    status 401
    return { error: "Invalid API key" }.to_json
  rescue Telnyx::RateLimitError
    status 429
    return { error: "Rate limit exceeded. Please slow down." }.to_json
  rescue Telnyx::APIStatusError => e
    status e.status_code || 500
    return { error: e.message, status_code: e.status_code }.to_json
  rescue Telnyx::APIConnectionError
    status 503
    return { error: "Network error connecting to Telnyx" }.to_json
  rescue StandardError => e
    status 400
    return { error: e.message }.to_json
  end
end

# Health check endpoint
get "/health" do
  content_type :json
  { status: "ok" }.to_json
end
