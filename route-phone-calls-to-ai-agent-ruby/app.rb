# config/initializers/telnyx.rb
require 'telnyx'

Telnyx.api_key = ENV['TELNYX_API_KEY']

# app/controllers/webhooks_controller.rb
class WebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:inbound_call]

  def inbound_call
    event_data = request.raw_post
    event = JSON.parse(event_data)

    call_control_id = event.dig('data', 'call_control_id')
    from_number = event.dig('data', 'from')
    to_number = event.dig('data', 'to')
    event_type = event.dig('data', 'event_type')

    Rails.logger.info("Inbound call received: #{call_control_id} from #{from_number} to #{to_number}")

    case event_type
    when 'call.initiated'
      handle_call_initiated(call_control_id, from_number, to_number)
    when 'call.answered'
      handle_call_answered(call_control_id)
    when 'call.hangup'
      handle_call_hangup(call_control_id)
    else
      Rails.logger.warn("Unhandled event type: #{event_type}")
    end

    render json: { status: 'received' }, status: :ok
  rescue JSON::ParserError => e
    Rails.logger.error("Failed to parse webhook payload: #{e.message}")
    render json: { error: 'Invalid JSON' }, status: :bad_request
  rescue StandardError => e
    Rails.logger.error("Webhook processing error: #{e.message}")
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end

  private

  def handle_call_initiated(call_control_id, from_number, to_number)
    Rails.logger.info("Call initiated: #{call_control_id}")

    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.answer(call_control_id)
      Rails.logger.info("Call answered: #{call_control_id}")
    rescue Telnyx::AuthenticationError
      Rails.logger.error("Authentication failed: invalid API key")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error answering call: #{e.message}")
    rescue Telnyx::APIConnectionError
      Rails.logger.error("Network error connecting to Telnyx")
    end
  end

  def handle_call_answered(call_control_id)
    Rails.logger.info("Call answered: #{call_control_id}")

    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.start_recording(call_control_id)
      Rails.logger.info("Recording started: #{call_control_id}")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error starting recording: #{e.message}")
    end
  end

  def handle_call_hangup(call_control_id)
    Rails.logger.info("Call ended: #{call_control_id}")

    begin
      client = Telnyx::Client.new(api_key: ENV['TELNYX_API_KEY'])
      client.calls.actions.stop_recording(call_control_id)
      Rails.logger.info("Recording stopped: #{call_control_id}")
    rescue Telnyx::APIStatusError => e
      Rails.logger.error("API error stopping recording: #{e.message}")
    end
  end
end

# config/routes.rb
Rails.application.routes.draw do
  post 'webhooks/inbound_call', to: 'webhooks#inbound_call'
end

# .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE

# Gemfile
source 'https://rubygems.org'
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby '3.0.0'

gem 'rails', '~> 6.1.0'
gem 'telnyx-ruby'
gem 'dotenv-rails'
