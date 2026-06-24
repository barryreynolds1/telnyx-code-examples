<?php
// app/Services/TelnyxIoTService.php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\TelnyxException;

class TelnyxIoTService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: config('telnyx.api_key'));
    }

    public function listSimCards(array $params = []): array
    {
        try {
            $response = $this->client->simCards->list($params);
            
            return array_map(function ($sim) {
                return [
                    'id' => $sim->id,
                    'iccid' => $sim->iccid,
                    'status' => $sim->status,
                    'sim_card_group_id' => $sim->sim_card_group_id ?? null,
                    'type' => $sim->type ?? null,
                ];
            }, $response->data ?? []);
        } catch (TelnyxException $e) {
            throw $e;
        }
    }

    public function getSimCard(string $simCardId): array
    {
        try {
            $response = $this->client->simCards->retrieve($simCardId);
            
            return [
                'id' => $response->data->id,
                'iccid' => $response->data->iccid,
                'status' => $response->data->status,
                'sim_card_group_id' => $response->data->sim_card_group_id ?? null,
                'type' => $response->data->type ?? null,
                'phone_number' => $response->data->phone_number ?? null,
            ];
        } catch (TelnyxException $e) {
            throw $e;
        }
    }

    public function activateSimCard(string $simCardId): array
    {
        try {
            $response = $this->client->simCards->activate($simCardId);
            
            return [
                'id' => $response->data->id,
                'status' => $response->data->status,
                'iccid' => $response->data->iccid,
            ];
        } catch (TelnyxException $e) {
            throw $e;
        }
    }

    public function getNetworkUsage(string $simCardId): array
    {
        try {
            $response = $this->client->request(
                'GET',
                "/v2/sim_cards/{$simCardId}/network_usage"
            );
            
            return $response->json() ?? [];
        } catch (TelnyxException $e) {
            throw $e;
        }
    }
}
