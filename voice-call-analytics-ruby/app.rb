#!/usr/bin/env ruby
"""Production-ready Sinatra application for call analytics via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "sqlite3"
require "json"
require "time"

# Initialize Telnyx client with the new SDK pattern
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# Database helper to initialize connection
def db
  @db ||= SQLite3::Database.new "db/analytics.db"
  @db.results_as_hash = true
  @db
end

# Helper to initiate an outbound call
def initiate_call(to_number)
  from_number = ENV["TELNYX_PHONE_NUMBER"]
  connection_id = ENV["TELNYX_CONNECTION_ID"]
  
  raise "TELNYX_PHONE_NUMBER not set" unless from_number
  raise "TELNYX_CONNECTION_ID not set" unless connection_id
  
  # Validate E.164 format
  raise "Phone number must be in E.164 format (e.g., +15551234567)" unless to_number.start_with?("+")
  
  # Initiate call using Call Control API
  response = client.calls.dial(
    from_: from_number,
    to: to_number,
    connection_id: connection_id
  )
  
  # Extract call_control_id from response
  call_control_id = response.data.call_control_id
  
  # Store call record in database
  db.execute(
    "INSERT INTO calls (call_control_id, from_number, to_number, status, started_at) VALUES (?, ?, ?, ?, ?)",
    [call_control_id, from_number, to_number, "initiated", Time.now.iso8601]
  )
  
  # Return serializable data
  {
    call_control_id: call_control_id,
    from: from_number,
    to: to_number,
    status: "initiated"
  }
end

# Helper to record call event
def record_call_event(call_control_id, event_type, event_data = {})
  db.execute(
    "INSERT INTO call_events (call_control_id, event_type, event_data) VALUES (?, ?, ?)",
    [call_control_id, event_type, event_data.to_json]
  )
end

# Helper to update call status
def update_call_status(call_control_id, status, ended_at = nil)
  if ended_at
    db.execute(
      "UPDATE calls SET status = ?, ended_at = ? WHERE call_control_id = ?",
      [status, ended_at, call_control_id]
    )
  else
    db.execute(
      "UPDATE calls SET status = ? WHERE call_control_id = ?",
      [status, call_control_id]
    )
  end
end

# Helper to calculate call duration
def calculate_duration(call_control_id)
  result = db.execute(
    "SELECT started_at, ended_at FROM calls WHERE call_control_id = ?",
    [call_control_id]
  ).first
  
  return 0 unless result && result["started_at"] && result["ended_at"]
  
  start_time = Time.parse(result["started_at"])
  end_time = Time.parse(result["ended_at"])
  (end_time - start_time).to_i
end

# Route to initiate a call
post "/calls/initiate" do
  content_type :json
  data = JSON.parse(request.body.read)
  
  to_number = data["to"]
  
  return [400, { error: "Missing required field: 'to'" }.to_json] unless to_number
  
  begin
    result = initiate_call(to_number)
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

# Webhook endpoint to receive call events
post "/webhooks/call" do
  content_type :json
  
  begin
    payload = JSON.parse(request.body.read)
    event_type = payload["data"]["event_type"]
    call_control_id = payload["data"]["call_control_id"]
    
    # Record the event in database
    record_call_event(call_control_id, event_type, payload["data"])
    
    # Update call status based on event type
    case event_type
    when "call.answered"
      update_call_status(call_control_id, "answered")
    when "call.hangup"
      update_call_status(call_control_id, "completed", Time.now.iso8601)
    when "call.initiated"
      update_call_status(call_control_id, "initiated")
    end
    
    # Return 200 OK to acknowledge receipt
    [200, { status: "received" }.to_json]
  rescue StandardError => e
    [400, { error: e.message }.to_json]
  end
end

# Route to get call analytics
get "/analytics/calls" do
  content_type :json
  
  begin
    # Fetch all calls with calculated duration
    calls = db.execute("SELECT * FROM calls ORDER BY created_at DESC")
    
    calls_with_duration = calls.map do |call|
      duration = calculate_duration(call["call_control_id"])
      {
        call_control_id: call["call_control_id"],
        from: call["from_number"],
        to: call["to_number"],
        status: call["status"],
        duration_seconds: duration,
        started_at: call["started_at"],
        ended_at: call["ended_at"],
        created_at: call["created_at"]
      }
    end
    
    [200, calls_with_duration.to_json]
  rescue StandardError => e
    [500, { error: e.message }.to_json]
  end
end

# Route to get analytics summary
get "/analytics/summary" do
  content_type :json
  
  begin
    total_calls = db.execute("SELECT COUNT(*) as count FROM calls").first["count"]
    completed_calls = db.execute("SELECT COUNT(*) as count FROM calls WHERE status = 'completed'").first["count"]
    
    total_duration = db.execute(
      "SELECT SUM(CAST((julianday(ended_at) - julianday(started_at)) * 86400 AS INTEGER)) as total FROM calls WHERE ended_at IS NOT NULL"
    ).first["total"] || 0
    
    average_duration = completed_calls > 0 ? (total_duration / completed_calls).to_i : 0
    
    summary = {
      total_calls: total_calls,
      completed_calls: completed_calls,
      pending_calls: total_calls - completed_calls,
      total_duration_seconds: total_duration,
      average_duration_seconds: average_duration
    }
    
    [200, summary.to_json]
  rescue StandardError => e
    [500, { error: e.message }.to_json]
  end
end

# Route to get call details with events
get "/analytics/calls/:call_control_id" do
  content_type :json
  call_control_id = params[:call_control_id]
  
  begin
    call = db.execute(
      "SELECT * FROM calls WHERE call_control_id = ?",
      [call_control_id]
    ).first
    
    return [404, { error: "Call not found" }.to_json] unless call
    
    events = db.execute(
      "SELECT event_type, event_data, created_at FROM call_events WHERE call_control_id = ? ORDER BY created_at ASC",
      [call_control_id]
    )
    
    duration = calculate_duration(call_control_id)
    
    call_details = {
      call_control_id: call["call_control_id"],
      from: call["from_number"],
      to: call["to_number"],
      status: call["status"],
      duration_seconds: duration,
      started_at: call["started_at"],
      ended_at: call["ended_at"],
      created_at: call["created_at"],
      events: events.map do |event|
        {
          event_type: event["event_type"],
          event_data: JSON.parse(event["event_data"]),
          created_at: event["created_at"]
        }
      end
    }
    
    [200, call_details.to_json]
  rescue StandardError => e
    [500, { error: e.message }.to_json]
  end
end

# Health check endpoint
get "/health" do
  content_type :json
  [200, { status: "ok" }.to_json]
end
