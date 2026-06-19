#!/usr/bin/env ruby
# config/initializers/telnyx.rb
require 'telnyx'

TELNYX_CLIENT = Telnyx::Client.new(api_key: ENV["TELNYX_API_KEY"])

# app/services/sip_connection_service.rb
class SipConnectionService
  def initialize(client = TELNYX_CLIENT)
    @client = client
  end

  def create_connection(name:, username:, password:, sip_endpoint:)
    raise ArgumentError, "Name is required" if name.blank?
    raise ArgumentError, "Username is required" if username.blank?
    raise ArgumentError, "Password is required" if password.blank?
    raise ArgumentError, "SIP endpoint is required" if sip_endpoint.blank?

    response = @client.sip_connections.create(
      connection_name: name,
      inbound: {
        sip_subdomain: name.downcase.gsub(/[^a-z0-9]/, ""),
      },
      outbound: {
        outbound_voice_profile_id: nil,
        sip_address: sip_endpoint,
      },
      credentials: {
        authentication: {
          authentication_type: "credential",
          username: username,
          password: password,
        }
      }
    )

    {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.authentication&.username,
      sip_endpoint: response.data.outbound&.sip_address,
      status: response.data.active ? "active" : "inactive",
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def list_connections(limit: 10, after: nil)
    params = { limit: limit }
    params[:after] = after if after.present?

    response = @client.sip_connections.list(**params)

    {
      connections: response.data.map do |conn|
        {
          id: conn.id,
          name: conn.connection_name,
          username: conn.credentials&.authentication&.username,
          sip_endpoint: conn.outbound&.sip_address,
          status: conn.active ? "active" : "inactive",
          created_at: conn.created_at,
        }
      end,
      pagination: {
        limit: response.meta&.pagination&.page_size,
        after: response.meta&.pagination&.after,
      }
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def get_connection(connection_id)
    raise ArgumentError, "Connection ID is required" if connection_id.blank?

    response = @client.sip_connections.retrieve(connection_id)

    {
      id: response.data.id,
      name: response.data.connection_name,
      username: response.data.credentials&.authentication&.username,
      sip_endpoint: response.data.outbound&.sip_address,
      status: response.data.active ? "active" : "inactive",
      created_at: response.data.created_at,
      updated_at: response.data.updated_at,
    }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end

  def delete_connection(connection_id)
    raise ArgumentError, "Connection ID is required" if connection_id.blank?

    @client.sip_connections.delete(connection_id)
    { success: true, message: "SIP connection deleted successfully" }
  rescue Telnyx::AuthenticationError
    raise "Invalid API key. Check TELNYX_API_KEY environment variable."
  rescue Telnyx::APIStatusError => e
    raise "Telnyx API error: #{e.message} (Status: #{e.status_code})"
  rescue Telnyx::APIConnectionError
    raise "Network error connecting to Telnyx. Check your internet connection."
  end
end

# app/controllers/sip_connections_controller.rb
class SipConnectionsController < ApplicationController
  before_action :initialize_service

  def index
    begin
      result = @service.list_connections(limit: params[:limit] || 10)
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

  def create
    begin
      required_params = [:name, :username, :password, :sip_endpoint]
      missing_params = required_params.select { |p| params[p].blank? }
      
      if missing_params.any?
        return render json: { error: "Missing required fields: #{missing_params.join(', ')}" }, status: :bad_request
      end

      result = @service.create_connection(
        name: params[:name],
        username: params[:username],
        password: params[:password],
        sip_endpoint: params[:sip_endpoint]
      )
      render json: result, status: :created
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  def show
    begin
      result = @service.get_connection(params[:id])
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  def destroy
    begin
      result = @service.delete_connection(params[:id])
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
    rescue StandardError => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  private

  def initialize_service
    @service = SipConnectionService.new
  end
end

# config/routes.rb
Rails.application.routes.draw do
  resources :sip_connections, only: [:index, :create, :show, :destroy]
end

# .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_SIP_USERNAME=your_sip_username
TELNYX_SIP_PASSWORD=your_sip_password
TELNYX_SIP_ENDPOINT=192.0.2.1
