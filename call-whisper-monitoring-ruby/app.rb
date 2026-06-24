#!/usr/bin/env ruby
"""Production-ready Sinatra application for whisper prompt calls via Telnyx."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key from environment
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# Helper function to initiate a call with whisper prompt
def initiate_call_with_whisper(to_number, whisper_text, client)
  """
  Initiate an outbound call and prepare to play a whisper prompt.
  
  The whisper prompt is played to the caller before the call connects
  to the recipient. This is useful for agent context or disclaimers.
  """
  from_number = ENV["TELNYX_PHONE_NUMBER"]
  connection_id = ENV["TELNYX_CONNECTION_ID"]
  
  unless from_number && connection_id
    raise "Missing required environment variables: TELNYX_PHONE_NUMBER or TELNYX_CONNECTION_ID"
  end
  
  # Validate E.164 format to prevent API errors
  unless to_number.start_with?("+")
    raise "Phone number must be in E.164 format (e.g., +15551234567)"
  end
  
  # Initiate the call using client.calls.dial()
  # connection_id is REQUIRED and comes from your Call Control Application
  # Do NOT pass call_control_id to dial() — it is returned in the response
  response = client.calls.dial(
    from_: from_number,
    to: to_number,
    connection_id: connection_id
  )
  
  # Extract call_control_id from response — use it for subsequent actions
  call_control_id = response.data.call_control_id
  
  # Return serializable data (SDK objects are NOT JSON-serializable)
  {
    call_control_id: call_control_id,
    from: from_number,
    to: to_number,
    whisper_text: whisper_text,
    status: "initiated"
  }
end

# Helper function to play whisper prompt to caller
def play_whisper_prompt(call_control_id, whisper_text, client)
  """
  Play a text-to-speech message to the caller before connecting to recipient.
  
  This uses the speak action to play audio. In production, you would typically
  trigger this from a webhook event (call.answered) to ensure the call is ready.
  """
  response = client.calls.actions.speak(
    call_control_id: call_control_id,
    payload: whisper_text,
    voice: "female"
  )
  
  {
    call_control_id: call_control_id,
    action: "speak",
    status: "queued"
  }
end

# Helper function to transfer call to recipient after whisper
def transfer_call(call_control_id, to_number, client)
  """
  Transfer the call to the final recipient after whisper prompt completes.
  
  This is typically triggered by a call.speak.ended webhook event.
  """
  response = client.calls.actions.transfer(
    call_control_id: call_control_id,
    to: to_number
  )
  
  {
    call_control_id: call_control_id,
    action: "transfer",
    to: to_number,
    status: "initiated"
  }
end

# Sinatra route to initiate a call with whisper prompt
post "/calls/initiate-whisper" do
  content_type :json
  
  data = JSON.parse(request.body.read) rescue {}
  
  unless data["to"] && data["whisper_text"]
    return [400, { error: "Missing required fields: 'to' and 'whisper_text'" }.to_json]
  end
  
  to_number = data["to"]
  whisper_text = data["whisper_text"]
  
  begin
    result = initiate_call_with_whisper(to_number, whisper_text, client)
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

# Webhook endpoint to handle call events
post "/webhooks/call" do
  content_type :json
  
  payload = JSON.parse(request.body.read) rescue {}
  event_type = payload.dig("data", "event_type")
  call_control_id = payload.dig("data", "call_control_id")
  
  case event_type
  when "call.answered"
    # Call has been answered by the caller — play whisper prompt
    whisper_text = payload.dig("data", "custom_headers", "whisper_text") || "Please wait while we connect your call."
    
    begin
      play_whisper_prompt(call_control_id, whisper_text, client)
      [200, { status: "whisper_queued" }.to_json]
    rescue => e
      [500, { error: e.message }.to_json]
    end
    
  when "call.speak.ended"
    # Whisper prompt has finished — transfer to recipient
    to_number = payload.dig("data", "custom_headers", "transfer_to")
    
    if to_number
      begin
        transfer_call(call_control_id, to_number, client)
        [200, { status: "transfer_initiated" }.to_json]
      rescue => e
        [500, { error: e.message }.to_json]
      end
    else
      [400, { error: "Missing transfer_to in custom headers" }.to_json]
    end
    
  when "call.hangup"
    # Call has ended — log for cleanup
    [200, { status: "call_ended", call_control_id: call_control_id }.to_json]
    
  else
    # Acknowledge other events without processing
    [200, { status: "acknowledged" }.to_json]
  end
end

# Health check endpoint
get "/health" do
  content_type :json
  { status: "ok" }.to_json
end
