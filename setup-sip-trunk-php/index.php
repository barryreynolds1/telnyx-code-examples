<?php
// app/Services/SipTrunkingService.php

namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class SipTrunkingService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    public function createSipConnection(
        string $name,
        string $username,
        string $password,
        string $sipAddress
    ): array {
        $response = $this->client->sip_connections->create([
            'connection_name' => $name,
            'active' => true,
            'credentials' => [
                'sip_username' => $username,
                'sip_password' => $password,
            ],
            'inbound' => [
                'sip_subdomain' => 'telnyx',
            ],
            'outbound' => [
                'outbound_voice_profile_id' => null,
            ],
        ]);

        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
            'created_at' => $response->data->created_at,
        ];
    }

    public function listSipConnections(): array
    {
        $response = $this->client->sip_connections->list();

        return array_map(function ($connection) {
            return [
                'id' => $connection->id,
                'name' => $connection->connection_name,
                'username' => $connection->credentials->sip_username ?? null,
                'active' => $connection->active,
                'created_at' => $connection->created_at,
            ];
        }, $response->data);
    }

    public function getSipConnection(string $connectionId): array
    {
        $response = $this->client->sip_connections->retrieve($connectionId);

        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
            'created_at' => $response->data->created_at,
            'inbound' => $response->data->inbound,
            'outbound' => $response->data->outbound,
        ];
    }

    public function updateSipConnection(string $connectionId, array $updates): array
    {
        $response = $this->client->sip_connections->update($connectionId, $updates);

        return [
            'id' => $response->data->id,
            'name' => $response->data->connection_name,
            'username' => $response->data->credentials->sip_username ?? null,
            'active' => $response->data->active,
        ];
    }

    public function deleteSipConnection(string $connectionId): bool
    {
        $this->client->sip_connections->delete($connectionId);
        return true;
    }
}

// app/Http/Controllers/SipConnectionController.php

namespace App\Http\Controllers;

use App\Services\SipTrunkingService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Telnyx\Exception\ApiException;
use Telnyx\Exception\AuthenticationException;
use Telnyx\Exception\RateLimitException;

class SipConnectionController extends Controller
{
    private SipTrunkingService $sipService;

    public function __construct(SipTrunkingService $sipService)
    {
        $this->sipService = $sipService;
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'username' => 'required|string|max:255',
            'password' => 'required|string|min:8',
            'sip_address' => 'required|string',
        ]);

        try {
            $connection = $this->sipService->createSipConnection(
                $validated['name'],
                $validated['username'],
                $validated['password'],
                $validated['sip_address']
            );

            return response()->json($connection, 201);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (RateLimitException) {
            return response()->json(['error' => 'Rate limit exceeded'], 429);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage(), 'status_code' => $e->getHttpStatus()],
                $e->getHttpStatus()
            );
        }
    }

    public function index(): JsonResponse
    {
        try {
            $connections = $this->sipService->listSipConnections();
            return response()->json($connections);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    public function show(string $id): JsonResponse
    {
        try {
            $connection = $this->sipService->getSipConnection($id);
            return response()->json($connection);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    public function update(Request $request, string $id): JsonResponse
    {
        $validated = $request->validate([
            'active' => 'sometimes|boolean',
            'password' => 'sometimes|string|min:8',
        ]);

        try {
            $connection = $this->sipService->updateSipConnection($id, $validated);
            return response()->json($connection);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }

    public function destroy(string $id): JsonResponse
    {
        try {
            $this->sipService->deleteSipConnection($id);
            return response()->json(['message' => 'Connection deleted successfully']);
        } catch (AuthenticationException) {
            return response()->json(['error' => 'Invalid API key'], 401);
        } catch (ApiException $e) {
            return response()->json(
                ['error' => $e->getMessage()],
                $e->getHttpStatus()
            );
        }
    }
}

// routes/api.php

use App\Http\Controllers\SipConnectionController;
use Illuminate\Support\Facades\Route;

Route::apiResource('sip-connections', SipConnectionController::class);

// config/services.php (add to existing array)

'telnyx' => [
    'api_key' => env('TELNYX_API_KEY'),
    'phone_number' => env('TELNYX_PHONE_NUMBER'),
    'sip_username' => env('SIP_USERNAME'),
    'sip_password' => env('SIP_PASSWORD'),
    'sip_endpoint' => env('SIP_ENDPOINT'),
],
