# config/initializers/telnyx.rb
require 'telnyx'

Telnyx.api_key = ENV['TELNYX_API_KEY']

# app/models/inbound_message.rb
class InboundMessage < ApplicationRecord
  validates :message_id, :from_number, :to_number, presence: true
  validates :message_id, uniqueness: true
end

# app/controllers/webhooks_controller.rb
class WebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:sms]

  def sms
    event_type = params.dig(:data, :event_type)
    
    if event_type == 'message.received'
      process_inbound_message
      render json: { success: true }, status: :ok
    else
      render json: { success: false, error: 'Unsupported event type' }, status: :unprocessable_entity
    end
  rescue StandardError => e
    Rails.logger.error("Webhook processing error: #{e.message}")
    render json: { error: e.message }, status: :internal_server_error
  end

  private

  def process_inbound_message
    message_data = params.dig(:data, :payload)
    return unless message_data

    from_number = message_data.dig(:from, :phone_number)
    to_number = message_data.dig(:to, 0, :phone_number)
    message_id = message_data[:id]
    text = message_data[:text]
    received_at = message_data[:received_at]

    raise ArgumentError, 'Missing required fields' unless from_number && to_number && message_id

    InboundMessage.create!(
      message_id: message_id,
      from_number: from_number,
      to_number: to_number,
      text: text,
      received_at: received_at
    )

    Rails.logger.info("Inbound SMS received from #{from_number}: #{text}")
  end
end

# config/routes.rb
Rails.application.routes.draw do
  post 'webhooks/sms', to: 'webhooks#sms'
end

# app/services/messaging_profile_service.rb
class MessagingProfileService
  def self.update_webhook_url(webhook_url)
    profiles = Telnyx::MessagingProfile.list
    profile = profiles.data.first

    return { error: 'No Messaging Profile found' } unless profile

    profile.webhook_url = webhook_url
    profile.webhook_api_version = '2'
    profile.save

    { success: true, profile_id: profile.id }
  rescue Telnyx::AuthenticationError
    { error: 'Invalid API key' }
  rescue Telnyx::APIStatusError => e
    { error: "API error: #{e.message}", status_code: e.status_code }
  rescue Telnyx::APIConnectionError
    { error: 'Network error connecting to Telnyx' }
  end
end

# .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
WEBHOOK_URL=https://your-domain.com/webhooks/sms
