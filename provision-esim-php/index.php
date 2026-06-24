<?php
// app/Services/EsimProvisioningService.php

namespace App\Services;

use App\Models\EsimProfile;
use Telnyx\Client;
use Telnyx\Exception\ApiException;

class EsimProvisioningService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: config('telnyx.api_key'));
    }

    public function provisionProfile(string $deviceName, array $metadata = []): array
    {
        $response = $this->client->simCards->list([
            'filter' => ['status' => 'pending'],
            'page' => ['size' => 1],
        ]);

        if (empty($response->data)) {
            throw new \Exception('No available eSIM profiles from Telnyx');
        }

        $simCard = $response->data[0];

        $profile = EsimProfile::create([
            'iccid' => $simCard->iccid,
            'status' => 'provisioned',
            'device_name' => $deviceName,
            'activation_code' => $this->generateActivationCode(),
            'metadata' => $metadata,
        ]);

        return [
            'id' => $profile->id,
            'iccid' => $profile->iccid,
            'status' => $profile->status,
            'device_name' => $profile->device_name,
            'activation_code' => $profile->activation_code,
        ];
    }

    public function activateProfile(int $profileId): array
    {
        $profile = EsimProfile::findOrFail($profileId);

        $response = $this->client->simCards->activate($profile->iccid, [
            'callback_url' => config('telnyx.base_url') . '/webhooks/esim-status',
        ]);

        $profile->update([
            'status' => 'active',
            'activated_at' => now(),
            'metadata' => array_merge($profile->metadata ?? [], [
                'sim_card_id' => $response->data->id ?? null,
            ]),
        ]);

        return [
            'id' => $profile->id,
            'iccid' => $profile->iccid,
            'status' => $profile->status,
            'activated_at' => $profile->activated_at,
        ];
    }

    public function getProfile(int $profileId): array
    {
        $profile = EsimProfile::findOrFail($profileId);

        return [
            'id' => $profile->id,
            'iccid' => $profile->iccid,
            'status' => $profile->status,
            'device_name' => $profile->device_name,
            'activation_code' => $profile->activation_code,
            'activated_at' => $profile->activated_at,
            'metadata' => $profile->metadata,
        ];
    }

    public function listProfiles(array $filters = []): array
    {
        $query = EsimProfile::query();

        if (isset($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (isset($filters['device_name'])) {
            $query->where('device_name', 'like', '%' . $filters['device_name'] . '%');
        }

        $profiles = $query->paginate(20);

        return [
            'data' => $profiles->map(fn($p) => [
                'id' => $p->id,
                'iccid' => $p->iccid,
                'status' => $p->status,
                'device_name' => $p->device_name,
                'activated_at' => $p->activated_at,
            ])->toArray(),
            'pagination' => [
                'total' => $profiles->total(),
                'per_page' => $profiles->perPage(),
                'current_page' => $profiles->currentPage(),
            ],
        ];
    }

    private function generateActivationCode(): string
    {
        return strtoupper(bin2hex(random_bytes(8)));
    }
}
