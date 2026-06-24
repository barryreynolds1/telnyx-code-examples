<?php
// app/Services/SipConnectionService.php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class SipConnectionService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: env('TELNYX_API_KEY'));
    }

    public function createConnection(
        string $name,
        string $username,
        string $password,
        string $endpoint
    ): array {
        if (!preg_match('/^[a-zA-Z0-9.-]+:\d+$/', $endpoint)) {
            throw new \InvalidArgumentException(
                'SIP endpoint must be in format: host:port (e.g., sip.example.com:5060)'
            );
        }

        $response = $this->client->sipConnections->create([
            'name' => $name,
            'outbound_voice_profile_id' => $this->getOrCreateOutboundProfile(),
            'inbound' => [
                'sip_subdomain' => strtolower(str_replace(' ', '-', $name)),
            ],
            'outbound' => [
                'outbound_voice_profile_id' => $this->getOrCreateOutboundProfile(),
            ],
            'credentials' => [
                'authentication' => 'credential',
                'credential_username' => $username,
                'credential_password' => $password,
            ],
        ]);

        return [
            'id' => $response->data->id,
            'name' => $response->data->name,
            'username' => $username,
            'sip_subdomain' => $response->data->inbound->sip_subdomain ?? null,
            'status' => 'created',
        ];
    }

    public function getConnection(string $connectionId): array
    {
        $response = $this->client->sipConnections->retrieve($connectionId);

        return [
            'id' => $response->data->id,
            'name' => $response->data->name,
            'username' => $response->data->credentials->credential_username ?? null,
            'sip_subdomain' => $response->data->inbound->sip_subdomain ?? null,
            'created_at' => $response->data->created_at ?? null,
        ];
    }

    public function listConnections(): array
    {
        $response = $this->client->sipConnections->list();

        return array_map(function ($connection) {
            return [
                'id' => $connection->id,
                'name' => $connection->name,
                'username' => $connection->credentials->credential_username ?? null,
                'sip_subdomain' => $connection->inbound->sip_subdomain ?? null,
            ];
        }, $response->data ?? []);
    }

    public function updateConnectionPassword(
        string $connectionId,
        string $newPassword
    ): array {
        $response = $this->client->sipConnections->update($connectionId, [
            'credentials' => [
                'credential_password' => $newPassword,
            ],
        ]);

        return [
            'id' => $response->data->id,
            'name' => $response->data->name,
            'password_updated' => true,
        ];
    }

    public function deleteConnection(string $connectionId): bool
    {
        $this->client->sipConnections->delete($connectionId);
        return true;
    }

    private function getOrCreateOutboundProfile(): string
    {
        try {
            $response = $this->client->outboundVoiceProfiles->list(['page' => ['size' => 1]]);
            if (!empty($response->data)) {
                return $response->data[0]->id;
            }
        } catch (\Exception $e) {
            // Profile list may fail; create a new one
        }

        $profile = $this->client->outboundVoiceProfiles->create([
            'name' => 'Default SIP Profile',
            'concurrency_limit' => 100,
            'daily_spend_limit' => 10000,
        ]);

        return $profile->data->id;
    }
}

// app/Http/Controllers/SipConnectionController.php

namespace App\Http\Controllers;

use App\Services\SipConnectionService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;

class SipConnectionController extends Controller
{
    private SipConnectionService $sipService;

    public function __construct(SipConnectionService $sipService)
    {
        $this->sipService = $sipService;
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'username' => 'required|string|max:255',
            'password' => 'required|string|min:8',
            'endpoint' => 'required|string|regex:/^[a-zA-Z0-9.-]+:\d+$/',
        ]);

        try {
            $connection = $this->sipService->createConnection(
                $validated['name'],
                $validated['username'],
                $validated['password'],
                $validated['endpoint']
            );

            return response()->json($connection, 201);
        } catch (\InvalidArgumentException $e) {
            return response()->json(['error' => $e->getMessage()], 400);
        }
    }

    public function show(string $connectionId): JsonResponse
    {
        try {
            $connection = $this->sipService->getConnection($connectionId);
            return response()->json($connection, 200);
        } catch (ApiException $e) {
            if ($e->getHttpStatus() === 404) {
                return response()->json(['error' => 'SIP connection not found'], 404);
            }
            throw $e;
        }
    }

    public function index(): JsonResponse
    {
        try {
            $connections = $this->sipService->listConnections();
            return response()->json($connections, 200);
        } catch (ApiException $e) {
            return response()->json(['error' => 'Failed to list connections'], 500);
        }
    }

    public function updatePassword(Request $request, string $connectionId): JsonResponse
    {
        $validated = $request->validate([
            'password' => 'required|string|min:8',
        ]);

        try {
            $result = $this->sipService->updateConnectionPassword(
                $connectionId,
                $validated['password']
            );
            return response()->json($result, 200);
        } catch (ApiException $e) {
            return response()->json(['error' => 'Failed to update password'], 500);
        }
    }

    public function destroy(string $connectionId): JsonResponse
    {
        try {
            $this->sipService->deleteConnection($connectionId);
            return response()->json(['message' => 'SIP connection deleted'], 200);
        } catch (ApiException $e) {
            return response()->json(['error' => 'Failed to delete connection'], 500);
        }
    }
}

// routes/api.php

use App\Http\Controllers\SipConnectionController;
use Illuminate\Support\Facades\Route;

Route::apiResource('sip-connections', SipConnectionController::class);
Route::patch('sip-connections/{connectionId}/password', [
    SipConnectionController::class,
    'updatePassword',
])->name('sip-connections.update-password');

// .env

TELNYX_API_KEY=YOUR_API_KEY_HERE
SIP_USERNAME=your_sip_username
SIP_PASSWORD=your_sip_password
SIP_ENDPOINT=sip.example.com:5060
TELNYX_PHONE_NUMBER=+15551234567

// config/services.php (add to existing file)

'telnyx' => [
    'api_key' => env('TELNYX_API_KEY'),
    'sip_username' => env('SIP_USERNAME'),
    'sip_password' => env('SIP_PASSWORD'),
    'sip_endpoint' => env('SIP_ENDPOINT'),
    'phone_number' => env('TELNYX_PHONE_NUMBER'),
],
