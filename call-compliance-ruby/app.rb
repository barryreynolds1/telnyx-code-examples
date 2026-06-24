#!/usr/bin/env ruby
"""Production-ready Sinatra application for call compliance with Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# In-memory call registry for tracking active calls and compliance data
# In production, use a database (PostgreSQL, MongoDB, etc.)
CALL_REGISTRY = {}
CALL_LOCK = Mutex.new

# Helper function to log call metadata for compliance
def log_call_metadata(call_control_id, metadata)
  """Store call metadata in registry for audit trail."""
  CALL_LOCK.synchronize do
    CALL_REGISTRY[call_control_id] ||= {}
    CALL_REGISTRY[call_control_id].merge!(metadata)
  end
end

# Helper function to retrieve call metadata
def get_call_metadata(call_control_id)
  """Retrieve stored call metadata."""
  CALL_LOCK.synchronize do
    CALL_REGISTRY[call_control_id] || {}
  end
end

# Helper function to initiate a compliant outbound call with recording
def initiate_compliant_call(to_number)
  """Dial outbound call and automatically start recording."""
  from_number = ENV["TELNYX_PHONE_NUMBER"]
  connection_id = ENV["TELNYX_CONNECTION_ID"]
  
  unless from_number && connection_id
    raise "TELNYX_PHONE_NUMBER and TELNYX_CONNECTION_ID must be set"
  end
  
  # Validate E.164 format
  unless to_number.start_with?("+")
    raise "Phone number must be in E.164 format (e.g., +15551234567)"
  end
  
  # Initiate the call
  response = client.calls.dial(
    from_: from_number,
    to: to_number,
    connection_id: connection_id
  )
  
  call_control_id = response.data.call_control_id
  
  # Log initial call metadata for compliance
  log_call_metadata(call_control_id, {
    call_control_id: call_control_id,
    from: from_number,
    to: to_number,
    initiated_at: Time.now.iso8601,
    status: "initiated",
    recording_enabled: true
  })
  
  # Return serializable response
  {
    call_control_id: call_control_id,
    from: from_number,
    to: to_number,
    status: "initiated"
  }
end

# Webhook endpoint for call.initiated event
post "/webhooks/call-initiated" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  call_control_id = payload.dig("data", "call_control_id")
  from_number = payload.dig("data", "from", "phone_number")
  to_number = payload.dig("data", "to", "phone_number")
  direction = payload.dig("data", "direction")
  
  # Log call initiation for compliance
  log_call_metadata(call_control_id, {
    call_control_id: call_control_id,
    from: from_number,
    to: to_number,
    direction: direction,
    initiated_at: Time.now.iso8601,
    status: "initiated"
  })
  
  puts "[COMPLIANCE] Call initiated: #{call_control_id} from #{from_number} to #{to_number}"
  
  json({ status: "received" })
end

# Webhook endpoint for call.answered event
post "/webhooks/call-answered" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  call_control_id = payload.dig("data", "call_control_id")
  
  # Update call metadata with answer time
  log_call_metadata(call_control_id, {
    answered_at: Time.now.iso8601,
    status: "answered"
  })
  
  # Start recording immediately upon answer for compliance
  begin
    client.calls.actions.start_recording(
      call_control_id,
      format: "wav"
    )
    
    log_call_metadata(call_control_id, {
      recording_started_at: Time.now.iso8601,
      recording_status: "active"
    })
    
    puts "[COMPLIANCE] Recording started for call: #{call_control_id}"
  rescue Telnyx::APIStatusError => e
    puts "[ERROR] Failed to start recording: #{e.message}"
  end
  
  json({ status: "received" })
end

# Webhook endpoint for call.hangup event
post "/webhooks/call-hangup" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  call_control_id = payload.dig("data", "call_control_id")
  hangup_reason = payload.dig("data", "hangup_reason")
  
  # Stop recording before call ends
  begin
    client.calls.actions.stop_recording(call_control_id)
    
    log_call_metadata(call_control_id, {
      recording_stopped_at: Time.now.iso8601,
      recording_status: "stopped"
    })
  rescue Telnyx::APIStatusError => e
    puts "[ERROR] Failed to stop recording: #{e.message}"
  end
  
  # Update call metadata with hangup information
  metadata = get_call_metadata(call_control_id)
  duration_seconds = if metadata[:answered_at] && metadata[:initiated_at]
    (Time.parse(metadata[:answered_at]) - Time.parse(metadata[:initiated_at])).to_i
  else
    0
  end
  
  log_call_metadata(call_control_id, {
    hangup_reason: hangup_reason,
    hangup_at: Time.now.iso8601,
    status: "completed",
    duration_seconds: duration_seconds
  })
  
  puts "[COMPLIANCE] Call completed: #{call_control_id} (#{duration_seconds}s, reason: #{hangup_reason})"
  
  json({ status: "received" })
end

# Webhook endpoint for call.recording.saved event
post "/webhooks/call-recording-saved" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  call_control_id = payload.dig("data", "call_control_id")
  recording_url = payload.dig("data", "recording_urls", 0)
  
  # Store recording URL for audit trail
  log_call_metadata(call_control_id, {
    recording_url: recording_url,
    recording_saved_at: Time.now.iso8601
  })
  
  puts "[COMPLIANCE] Recording saved for call #{call_control_id}: #{recording_url}"
  
  json({ status: "received" })
end

# HTTP endpoint to initiate a compliant outbound call
post "/calls/initiate" do
  data = JSON.parse(request.body.read) rescue {}
  
  to_number = data["to"]
  
  unless to_number
    return [400, { "Content-Type" => "application/json" }, 
            JSON.generate({ error: "Missing required field: 'to'" })]
  end
  
  begin
    result = initiate_compliant_call(to_number)
    [200, { "Content-Type" => "application/json" }, JSON.generate(result)]
  rescue Telnyx::AuthenticationError
    [401, { "Content-Type" => "application/json" }, 
     JSON.generate({ error: "Invalid API key" })]
  rescue Telnyx::RateLimitError
    [429, { "Content-Type" => "application/json" }, 
     JSON.generate({ error: "Rate limit exceeded. Please slow down." })]
  rescue Telnyx::APIStatusError => e
    [e.status_code || 500, { "Content-Type" => "application/json" }, 
     JSON.generate({ error: e.message, status_code: e.status_code })]
  rescue Telnyx::APIConnectionError
    [503, { "Content-Type" => "application/json" }, 
     JSON.generate({ error: "Network error connecting to Telnyx" })]
  rescue StandardError => e
    [400, { "Content-Type" => "application/json" }, 
     JSON.generate({ error: e.message })]
  end
end

# HTTP endpoint to retrieve call compliance metadata
get "/calls/:call_control_id/metadata" do
  call_control_id = params[:call_control_id]
  metadata = get_call_metadata(call_control_id)
  
  if metadata.empty?
    return [404, { "Content-Type" => "application/json" }, 
            JSON.generate({ error: "Call not found" })]
  end
  
  [200, { "Content-Type" => "application/json" }, JSON.generate(metadata)]
end

# HTTP endpoint to list all recorded calls (compliance audit)
get "/calls/audit/list" do
  audit_list = CALL_LOCK.synchronize do
    CALL_REGISTRY.map do |call_id, metadata|
      {
        call_control_id: call_id,
        from: metadata[:from],
        to: metadata[:to],
        direction: metadata[:direction],
        status: metadata[:status],
        duration_seconds: metadata[:duration_seconds],
        initiated_at: metadata[:initiated_at],
        answered_at: metadata[:answered_at],
        hangup_at: metadata[:hangup_at],
        recording_url: metadata[:recording_url],
        recording_status: metadata[:recording_status]
      }
    end
  end
  
  [200, { "Content-Type" => "application/json" }, JSON.generate(audit_list)]
end

# Health check endpoint
get "/health" do
  json({ status: "ok" })
end
