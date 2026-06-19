# config/routes.rb
Rails.application.routes.draw do
  post '/sim_cards/:id/activate', to: 'sim_cards#activate'
end
