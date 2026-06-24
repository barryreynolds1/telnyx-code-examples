#!/usr/bin/env ruby
"""Production-ready Sinatra application for warm transfer via Telnyx Voice API."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with the new SDK pattern
def telnyx_client
  Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
end

# In-memory store for call state (use Redis in production)
$call_state = {}

def initiate_call(to_number)
  """Initiate an outbound call and return call control ID."""
  response = telnyx_client.calls.dial(
    from_: ENV["TELNYX_PHONE_NUMBER"],
    to: to_number,
    connection_id: ENV["TELNYX_CONNECTION_ID"]
  )
  
  # Store call state for webhook handling
  call_control_id = response.data.call_control_id
  $call_state[call_control_id] = {
    status: "initiated",
    to: to_number,
    created_at: Time.now.to_i
  }
  
  {
    call_control_id: call_control_id,
    status: "initiated"
  }
end

def answer_call(call_control_id)
  """Answer an incoming call."""
  response = telnyx_client.calls.actions.answer(call_control_id)
  
  $call_state[call_control_id] ||= {}
  $call_state[call_control_id][:status] = "answered"
  
  {
    call_control_id: call_control_id,
    status: "answered"
  }
end

def speak_to_caller(call_control_id, message)
  """Play text-to-speech message to the caller."""
  response = telnyx_client.calls.actions.speak(
    call_control_id,
    payload: message,
    voice: "female",
    language: "en-US"
  )
  
  {
    call_control_id: call_control_id,
    message: message
  }
end

def transfer_call(call_control_id, transfer_to)
  """Transfer the call to another party."""
  response = telnyx_client.calls.actions.transfer(
    call_control_id,
    to: transfer_to
  )
  
  $call_state[call_control_id] ||= {}
  $call_state[call_control_id][:status] = "transferred"
  $call_state[call_control_id][:transferred_to] = transfer_to
  
  {
    call_control_id: call_control_id,
    status: "transferred",
    transferred_to: transfer_to
  }
end

def hangup_call(call_control_id)
  """Terminate the call."""
  response = telnyx_client.calls.actions.hangup(call_control_id)
  
  $call_state[call_control_id] ||= {}
  $call_state[call_control_id][:status] = "hangup"
  
  {
    call_control_id: call_control_id,
    status: "hangup"
  }
end

# Route to initiate a warm transfer call
post "/calls/initiate" do
  content_type :json
  
  data = JSON.parse(request.body.read)
  to_number = data["to"]
  
  if !to_number || !to_number.start_with?("+")
    return [400, { error: "Missing or invalid 'to' field. Use E.164 format." }.to_json]
  end
  
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
post "/webhooks/call-events" do
  content_type :json
  
  payload = JSON.parse(request.body.read)
  event_type = payload["data"]["event_type"]
  call_control_id = payload["data"]["call_control_id"]
  
  case event_type
  when "call.initiated"
    # Outbound call started
    $call_state[call_control_id] ||= {}
    $call_state[call_control_id][:status] = "initiated"
    
  when "call.answered"
    # Call connected — speak to the agent/caller
    $call_state[call_control_id] ||= {}
    $call_state[call_control_id][:status] = "answered"
    
    # Speak a message before transferring
    speak_to_caller(call_control_id, "Please hold while I connect you to the next available agent.")
    
  when "call.speak.ended"
    # TTS playback finished — now transfer
    if $call_state[call_control_id] && $call_state[call_control_id][:status] == "answered"
      transfer_call(call_control_id, ENV["TRANSFER_DESTINATION"])
    end
    
  when "call.hangup"
    # Call ended — clean up state
    $call_state.delete(call_control_id)
    
  end
  
  [200, { status: "received" }.to_json]
end

# Route to manually transfer a call (for testing)
post "/calls/:call_control_id/transfer" do
  content_type :json
  
  call_control_id = params[:call_control_id]
  data = JSON.parse(request.body.read)
  transfer_to = data["transfer_to"] || ENV["TRANSFER_DESTINATION"]
  
  if !transfer_to || !transfer_to.start_with?("+")
    return [400, { error: "Missing or invalid 'transfer_to' field. Use E.164 format." }.to_json]
  end
  
  begin
    result = transfer_call(call_control_id, transfer_to)
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

# Route to hangup a call
post "/calls/:call_control_id/hangup" do
  content_type :json
  
  call_control_id = params[:call_control_id]
  
  begin
    result = hangup_call(call_control_id)
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

# Route to get call state
get "/calls/:call_control_id" do
  content_type :json
  
  call_control_id = params[:call_control_id]
  state = $call_state[call_control_id]
  
  if state
    [200, state.to_json]
  else
    [404, { error: "Call not found" }.to_json]
  end
end
