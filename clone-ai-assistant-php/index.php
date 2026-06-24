<?php

// app/Services/AiAssistantService.php
namespace App\Services;

use Telnyx\Client;
use Telnyx\Exception\ApiException;

class AiAssistantService
{
    private Client $client;

    public function __construct()
    {
        $this->client = new Client(apiKey: getenv('TELNYX_API_KEY'));
    }

    public function cloneAssistant(string $assistantId, ?string $newName = null): array
    {
        if (empty($assistantId)) {
            throw new \InvalidArgumentException('Assistant ID cannot be empty');
        }

        $response = $this->client->ai_assistants->clone($assistantId, [
            'name' => $newName,
        ]);

        return [
            'id' => $response->data->id,
            'name' => $response->data->name,
            'model' => $response->data->model,
            'instructions' => $response->data->instructions,
            'enabled_features' => $response->data->enabled_features ?? [],
            'created_at' => $response->data->created_at,
        ];
    }

    public function getAssistant(string $assistantId): array
    {
        if (empty($assistantId)) {
            throw new \InvalidArgumentException('Assistant ID cannot be empty');
        }

        $response = $this->client->ai_assistants->retrieve($assistantId);

        return [
            'id' => $response->data->id,
            'name' => $response->data->name,
            'model' => $response->data->model,
            'instructions' => $response->data->instructions,
            'enabled_features' => $response->data->enabled_features ?? [],
            'created_at' => $response->data->created_at,
        ];
    }
}

// app/Http/Controllers/AiAssistantController.php
namespace App\Http\Controllers;

use App\Services\AiAssistantService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AiAssistantController extends Controller
{
    private AiAssistantService $assistantService;

    public function __construct(AiAssistantService $assistantService)
    {
        $this->assistantService = $assistantService;
    }

    public function clone(Request $request, string $assistantId): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'nullable|string|max:255',
        ]);

        try {
            $clonedAssistant = $this->assistantService->cloneAssistant(
                $assistantId,
                $validated['name'] ?? null
            );

            return response()->json([
                'success' => true,
                'data' => $clonedAssistant,
            ], 201);

        } catch (\InvalidArgumentException $e) {
            return response()->json([
                'error' => $e->getMessage(),
            ], 400);
        }
    }

    public function show(string $assistantId): JsonResponse
    {
        try {
            $assistant = $this->assistantService->getAssistant($assistantId);

            return response()->json([
                'success' => true,
                'data' => $assistant,
            ], 200);

        } catch (\InvalidArgumentException $e) {
            return response()->json([
                'error' => $e->getMessage(),
            ], 400);
        }
    }
}

// routes/api.php
use App\Http\Controllers\AiAssistantController;
use Illuminate\Support\Facades\Route;

Route::prefix('assistants')->group(function () {
    Route::get('{assistantId}', [AiAssistantController::class, 'show']);
    Route::post('{assistantId}/clone', [AiAssistantController::class, 'clone']);
});

// app/Exceptions/Handler.php
namespace App\Exceptions;

use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Illuminate\Http\JsonResponse;
use Telnyx\Exception\ApiException;
use Telnyx\Exception\AuthenticationException;
use Telnyx\Exception\RateLimitException;
use Throwable;

class Handler extends ExceptionHandler
{
    protected $dontFlash = [
        'current_password',
        'password',
        'password_confirmation',
    ];

    public function register(): void
    {
        $this->reportable(function (Throwable $e) {
            //
        });
    }

    public function render($request, Throwable $exception): JsonResponse
    {
        if ($exception instanceof AuthenticationException) {
            return response()->json([
                'error' => 'Invalid API key or authentication failed',
            ], 401);
        }

        if ($exception instanceof RateLimitException) {
            return response()->json([
                'error' => 'Rate limit exceeded. Please slow down.',
            ], 429);
        }

        if ($exception instanceof ApiException) {
            return response()->json([
                'error' => $exception->getMessage(),
                'status_code' => $exception->getCode(),
            ], $exception->getCode() ?: 500);
        }

        return response()->json([
            'error' => 'An unexpected error occurred',
        ], 500);
    }
}

// .env
TELNYX_API_KEY=your_actual_api_key_here
