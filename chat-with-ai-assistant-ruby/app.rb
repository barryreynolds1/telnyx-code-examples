#!/usr/bin/env ruby
# config/initializers/telnyx.rb
Telnyx.configure do |config|
  config.api_key = ENV["TELNYX_API_KEY"]
end

# app/services/ai_chat_service.rb
class AiChatService
  def initialize(assistant_id)
    @assistant_id = assistant_id
    @client = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])
  end

  def chat(messages)
    # Validate assistant ID is configured
    unless @assistant_id
      raise ArgumentError, "TELNYX_ASSISTANT_ID environment variable not set"
    end

    # Validate messages array is not empty
    if messages.blank? || !messages.is_a?(Array)
      raise ArgumentError, "Messages must be a non-empty array"
    end

    # Call the AI Assistant chat endpoint
    # messages format: [{ role: "user", content: "Hello" }]
    response = @client.ai_assistants.chat(
      @assistant_id,
      messages: messages
    )

    # Extract serializable data — SDK objects are NOT JSON-serializable
    {
      assistant_id: response.data.assistant_id,
      messages: response.data.messages.map do |msg|
        {
          role: msg.role,
          content: msg.content
        }
      end,
      created_at: response.data.created_at
    }
  end
end

# app/controllers/chat_controller.rb
class ChatController < ApplicationController
  skip_forgery_protection only: [:create]

  def index
    # Render the chat interface view
    render :index
  end

  def create
    # Extract messages from request body
    messages = params.require(:messages)

    unless messages.is_a?(Array) && messages.any?
      return render json: { error: "Messages array required and must not be empty" }, status: :bad_request
    end

    # Initialize the AI chat service with the configured assistant ID
    assistant_id = ENV["TELNYX_ASSISTANT_ID"]
    service = AiChatService.new(assistant_id)

    begin
      # Call the service to chat with the AI Assistant
      result = service.chat(messages)
      render json: result, status: :ok

    rescue Telnyx::AuthenticationError
      render json: { error: "Invalid API key" }, status: :unauthorized

    rescue Telnyx::RateLimitError
      render json: { error: "Rate limit exceeded. Please slow down." }, status: :too_many_requests

    rescue Telnyx::APIStatusError => e
      render json: { error: e.message, status_code: e.status_code }, status: e.status_code

    rescue Telnyx::APIConnectionError
      render json: { error: "Network error connecting to Telnyx" }, status: :service_unavailable

    rescue ArgumentError => e
      render json: { error: e.message }, status: :bad_request
    end
  end
end

# config/routes.rb
Rails.application.routes.draw do
  root 'chat#index'
  
  get 'chat/index'
  post 'chat', to: 'chat#create'
end

# Gemfile
source 'https://rubygems.org'
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby '3.2.0'

gem 'rails', '~> 7.0.0'
gem 'telnyx'
gem 'dotenv-rails'
gem 'puma', '~> 5.0'
gem 'sass-rails', '>= 6'
gem 'webpacker', '~> 5.0'
gem 'turbolinks-rails'
gem 'jbuilder', '~> 2.7'
gem 'redis', '~> 4.0'
gem 'bcrypt', '~> 3.1.7'
gem 'image_processing', '~> 1.2'
gem 'aws-sdk-s3', require: false
gem 'devise'
gem 'pundit', '~> 2.1'
gem 'pagy', '~> 4.10'

group :development, :test do
  gem 'byebug', platforms: [:mri, :mingw, :x64_mingw]
  gem 'rspec-rails'
  gem 'factory_bot_rails'
end

group :development do
  gem 'web-console', '>= 4.1.0'
  gem 'listen', '~> 3.3'
end

# .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_ASSISTANT_ID=YOUR_ASSISTANT_ID_HERE
