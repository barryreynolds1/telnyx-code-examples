#!/usr/bin/env ruby
# config/initializers/telnyx.rb
require 'telnyx'

TELNYX_CLIENT = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# app/services/call_service.rb
class CallService
  def self.initiate_call(to_number:)
    from_number = ENV["TELNYX_PHONE_NUMBER"]
    connection_id = ENV["TELNYX_CONNECTION_ID"]
    
    raise "TELNYX_PHONE_NUMBER not configured" unless from_number
    raise "TELNYX_CONNECTION_ID not configured" unless connection_id
    raise "Phone number must be in E.164 format (e.g., +15551234567)" unless to_number.start_with?("+")
    
    response = TELNYX_CLIENT.calls.dial(
      from_: from_number,
      to: to_number,
      connection_id: connection_id
    )
    
    {
      call_control_id: response.data.call_control_id,
      from: from_number,
      to: to_number,
      state: response.data.state
    }
  end
end

# app/controllers/calls_controller.rb
class CallsController < ApplicationController
  def initiate
    body = JSON.parse(request.body.read)
    to_number = body["to"]
    
    return render json: { error: "Missing required field: 'to'" }, status: :bad_request unless to_number
    
    result = CallService.initiate_call(to_number: to_number)
    render json: result, status: :ok
    
  rescue Telnyx::AuthenticationError
    render json: { error: "Invalid API key" }, status: :unauthorized
  rescue Telnyx::RateLimitError
    render json: { error: "Rate limit exceeded. Please slow down." }, status: :too_many_requests
  rescue Telnyx::APIStatusError => e
    render json: { error: e.message, status_code: e.status_code }, status: e.status_code
  rescue Telnyx::APIConnectionError
    render json: { error: "Network error connecting to Telnyx" }, status: :service_unavailable
  rescue StandardError => e
    render json: { error: e.message }, status: :bad_request
  end
end

# config/routes.rb
Rails.application.routes.draw do
  post "/calls/initiate", to: "calls#initiate"
end

# .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE

# Gemfile
source "https://rubygems.org"
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby "3.2.0"

gem "rails", "~> 7.0.0"
gem "telnyx-ruby"
gem "dotenv-rails"
