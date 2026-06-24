<?php
// app/Services/NumberLookupService.php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class NumberLookupService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    public function lookup(string $phoneNumber): array
    {
        if (!preg_match('/^\+\d{1,15}$/', $phoneNumber)) {
            throw new \InvalidArgumentException(
                'Phone number must be in E.164 format (e.g., +15551234567)'
            );
        }

        try {
            $response = $this->client->numberLookup->retrieve($phoneNumber);

            return [
                'phone_number' => $response->data->phone_number ?? $phoneNumber,
                'carrier_name' => $response->data->carrier_name ?? 'Unknown',
                'carrier_type' => $response->data->carrier_type ?? 'Unknown',
                'country_code' => $response->data->country_code ?? null,
                'number_type' => $response->data->number_type ?? 'Unknown',
                'portability_status' => $response->data->portability_status ?? 'Unknown',
            ];
        } catch (ApiException $e) {
            throw new \Exception('Number lookup failed: ' . $e->getMessage(), $e->getCode(), $e);
        }
    }
}
