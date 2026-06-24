#!/usr/bin/env ruby
"""Production-ready Sinatra app for hold music with Telnyx Voice API."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with the new SDK pattern
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# In-memory store for active calls (use Redis in production)
$active_calls = {}

# Configure Sinatra
set :port, 4567
set :bind, "0.0.0.0"

# Helper function to initiate an outbound call
def initiate_call(to_number, client)
  """Initiate an outbound call and return call_control_id."""
  from_number = ENV["TELNYX_PHONE_NUMBER"]
  connection_id = ENV["TELNYX_CONNECTION_ID"]
  
  unless from_number && connection_id
    raise ArgumentError, "TELNYX_PHONE_NUMBER and TELNYX_CONNECTION_ID must be set"
  end
  
  # Validate E.164 format
  unless to_number.start_with?("+")
    raise ArgumentError, "Phone number must be in E.164 format (e.g., +15551234567)"
  end
  
  # Use client.calls.dial() — returns CallDialResponse
  response = client.calls.dial(
    from_: from_number,
    to: to_number,
    connection_id: connection_id
  )
  
  # Extract call_control_id from response — this is returned, not passed in
  {
    call_control_id: response.data.call_control_id,
    from: from_number,
    to: to_number
  }
end

# Helper function to start hold music playback
def start_hold_music(call_control_id, client)
  """Stream hold music to an active call."""
  hold_music_url = ENV["HOLD_MUSIC_URL"]
  
  unless hold_music_url
    raise ArgumentError, "HOLD_MUSIC_URL environment variable not set"
  end
  
  # Use client.calls.actions.playback_start() to stream audio
  response = client.calls.actions.playback_start(
    call_control_id,
    audio_url: hold_music_url
  )
  
  {
    call_control_id: response.data.call_control_id,
    state: response.data.state
  }
end

# Helper function to stop hold music
def stop_hold_music(call_control_id, client)
  """Stop audio playback on a call."""
  response = client.calls.actions.playback_stop(call_control_id)
  
  {
    call_control_id: response.data.call_control_id,
    state: response.data.state
  }
end

# Helper function to hangup a call
def hangup_call(call_control_id, client)
  """Terminate an active call."""
  response = client.calls.actions.hangup(call_control_id)
  
  {
    call_control_id: response.data.call_control_id,
    state: response.data.state
  }
end

# POST /calls/initiate — Initiate an outbound call
post "/calls/initiate" do
  content_type :json
  
  data = JSON.parse(request.body.read) rescue {}
  
  to_number = data["to"]
  
  unless to_number
    return [400, { error: "Missing required field: 'to'" }.to_json]
  end
  
  begin
    result = initiate_call(to_number, client)
    
    # Store call in memory for webhook correlation
    $active_calls[result[:call_control_id]] = {
      to: to_number,
      from: result[:from],
      initiated_at: Time.now.to_i,
      state: "initiated"
    }
    
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

# POST /calls/:call_control_id/hold — Start hold music on a call
post "/calls/:call_control_id/hold" do
  content_type :json
  call_control_id = params[:call_control_id]
  
  unless $active_calls[call_control_id]
    return [404, { error: "Call not found" }.to_json]
  end
  
  begin
    result = start_hold_music(call_control_id, client)
    
    # Update call state
    $active_calls[call_control_id][:state] = "on_hold"
    
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

# POST /calls/:call_control_id/resume — Stop hold music and resume call
post "/calls/:call_control_id/resume" do
  content_type :json
  call_control_id = params[:call_control_id]
  
  unless $active_calls[call_control_id]
    return [404, { error: "Call not found" }.to_json]
  end
  
  begin
    result = stop_hold_music(call_control_id, client)
    
    # Update call state
    $active_calls[call_control_id][:state] = "active"
    
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

# POST /calls/:call_control_id/hangup — Terminate a call
post "/calls/:call_control_id/hangup" do
  content_type :json
  call_control_id = params[:call_control_id]
  
  unless $active_calls[call_control_id]
    return [404, { error: "Call not found" }.to_json]
  end
  
  begin
    result = hangup_call(call_control_id, client)
    
    # Remove call from memory
    $active_calls.delete(call_control_id)
    
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

# POST /webhooks/call — Receive call state change events
post "/webhooks/call" do
  content_type :json
  
  payload = JSON.parse(request.body.read) rescue {}
  event_type = payload["data"]&.dig("event_type")
  call_control_id = payload["data"]&.dig("call_control_id")
  
  # Log event for debugging
  puts "[#{Time.now}] Webhook: #{event_type} for call #{call_control_id}"
  
  case event_type
  when "call.initiated"
    # Call started — update state
    if $active_calls[call_control_id]
      $active_calls[call_control_id][:state] = "initiated"
    end
    
  when "call.answered"
    # Call answered — automatically start hold music
    if $active_calls[call_control_id]
      $active_calls[call_control_id][:state] = "answered"
      $active_calls[call_control_id][:answered_at] = Time.now.to_i
      
      # Automatically place on hold
      begin
        start_hold_music(call_control_id, client)
        $active_calls[call_control_id][:state] = "on_hold"
      rescue => e
        puts "[ERROR] Failed to start hold music: #{e.message}"
      end
    end
    
  when "call.hangup"
    # Call ended — clean up
    if $active_calls[call_control_id]
      $active_calls[call_control_id][:state] = "hangup"
      $active_calls[call_control_id][:ended_at] = Time.now.to_i
    end
    
  when "call.playback.started"
    # Hold music started
    if $active_calls[call_control_id]
      $active_calls[call_control_id][:playback_started] = true
    end
    
  when "call.playback.ended"
    # Hold music finished
    if $active_calls[call_control_id]
      $active_calls[call_control_id][:playback_started] = false
    end
  end
  
  # Always return 200 to acknowledge receipt
  [200, { status: "ok" }.to_json]
end

# GET /calls — List active calls
get "/calls" do
  content_type :json
  
  calls = $active_calls.map do |call_control_id, data|
    {
      call_control_id: call_control_id,
      to: data[:to],
      from: data[:from],
      state: data[:state],
      initiated_at: data[:initiated_at],
      answered_at: data[:answered_at],
      ended_at: data[:ended_at]
    }
  end
  
  [200, { calls: calls }.to_json]
end

# GET /health — Health check
get "/health" do
  content_type :json
  [200, { status: "ok" }.to_json]
end
