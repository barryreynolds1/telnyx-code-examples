#!/usr/bin/env ruby
"""Production-ready Sinatra application for voicemail with Telnyx Voice API."""

require "sinatra"
require "telnyx"
require "dotenv/load"
require "json"

# Initialize Telnyx client with API key
client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# In-memory storage for voicemail metadata (use a database in production)
voicemails = {}

# Configure Sinatra
set :port, 4567
set :bind, "0.0.0.0"

# Helper function to answer an inbound call
def answer_call(client, call_control_id)
  client.calls.actions.answer(call_control_id)
rescue Telnyx::APIStatusError => e
  puts "Error answering call: #{e.message}"
end

# Helper function to play a greeting and start recording
def play_greeting_and_record(client, call_control_id)
  # Play a greeting message
  client.calls.actions.speak(
    call_control_id,
    payload: "Please leave your message after the beep. Press pound when finished.",
    voice: "female",
    language: "en-US"
  )
  
  # Start recording the voicemail
  client.calls.actions.start_recording(
    call_control_id,
    format: "wav"
  )
rescue Telnyx::APIStatusError => e
  puts "Error playing greeting or starting recording: #{e.message}"
end

# Helper function to hang up the call
def hangup_call(client, call_control_id)
  client.calls.actions.hangup(call_control_id)
rescue Telnyx::APIStatusError => e
  puts "Error hanging up call: #{e.message}"
end

# Webhook endpoint to receive call events
post "/webhooks/call" do
  request.body.rewind
  payload = JSON.parse(request.body.read)
  
  event_type = payload.dig("data", "event_type")
  call_control_id = payload.dig("data", "call_control_id")
  from_number = payload.dig("data", "from")
  to_number = payload.dig("data", "to")
  
  puts "Received event: #{event_type} for call #{call_control_id}"
  
  case event_type
  when "call.initiated"
    # Inbound call received — answer and start voicemail
    answer_call(client, call_control_id)
    play_greeting_and_record(client, call_control_id)
    
    # Store call metadata
    voicemails[call_control_id] = {
      from: from_number,
      to: to_number,
      initiated_at: Time.now.iso8601,
      status: "recording"
    }
    
  when "call.answered"
    # Call was answered — update status
    if voicemails[call_control_id]
      voicemails[call_control_id][:status] = "answered"
    end
    
  when "call.dtmf.received"
    # DTMF digit received (e.g., # to end recording)
    digit = payload.dig("data", "dtmf_digit")
    if digit == "#"
      # Stop recording and hang up
      client.calls.actions.stop_recording(call_control_id)
      hangup_call(client, call_control_id)
      
      if voicemails[call_control_id]
        voicemails[call_control_id][:status] = "completed"
      end
    end
    
  when "call.recording.saved"
    # Recording is ready for download
    recording_url = payload.dig("data", "recording_urls", 0)
    if voicemails[call_control_id]
      voicemails[call_control_id][:recording_url] = recording_url
      voicemails[call_control_id][:saved_at] = Time.now.iso8601
    end
    
  when "call.hangup"
    # Call ended — finalize voicemail record
    if voicemails[call_control_id]
      voicemails[call_control_id][:status] = "ended"
      voicemails[call_control_id][:ended_at] = Time.now.iso8601
    end
  end
  
  # Return 200 OK to acknowledge webhook receipt
  status 200
  json({ status: "ok" })
end

# Endpoint to retrieve voicemail metadata
get "/voicemails/:call_control_id" do
  call_control_id = params[:call_control_id]
  
  if voicemails[call_control_id]
    json(voicemails[call_control_id])
  else
    status 404
    json({ error: "Voicemail not found" })
  end
end

# Endpoint to list all voicemails
get "/voicemails" do
  json(voicemails.map { |id, data| { call_control_id: id, **data } })
end

# Health check endpoint
get "/health" do
  json({ status: "ok" })
end

# Error handler for Telnyx API errors
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
