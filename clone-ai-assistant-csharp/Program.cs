// Program.cs
using TelnyxAssistantCloner.Configuration;
using TelnyxAssistantCloner.Services;

DotNetEnv.DotEnv.Load();

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var telnyxConfig = new TelnyxConfig();
builder.Services.AddSingleton(telnyxConfig);
builder.Services.AddScoped<AssistantService>();

builder.Services.AddHttpClient("TelnyxClient", client =>
{
    client.BaseAddress = new Uri(telnyxConfig.BaseUrl);
    client.DefaultRequestHeaders.Authorization = 
        new System.Net.Http.Headers.AuthenticationHeaderValue(
            "Bearer", telnyxConfig.ApiKey);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();

// ============================================================================

// Configuration/TelnyxConfig.cs
namespace TelnyxAssistantCloner.Configuration
{
    public class TelnyxConfig
    {
        public string ApiKey { get; set; }
        public string BaseUrl { get; set; }

        public TelnyxConfig()
        {
            ApiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY") 
                ?? throw new InvalidOperationException("TELNYX_API_KEY not set");
            BaseUrl = Environment.GetEnvironmentVariable("TELNYX_BASE_URL") 
                ?? "https://api.telnyx.com/v2";
        }
    }
}

// ============================================================================

// Services/AssistantService.cs
using System.Text.Json;
using System.Text.Json.Serialization;
using TelnyxAssistantCloner.Configuration;

namespace TelnyxAssistantCloner.Services
{
    public class AssistantService
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly TelnyxConfig _config;

        public AssistantService(IHttpClientFactory httpClientFactory, TelnyxConfig config)
        {
            _httpClientFactory = httpClientFactory;
            _config = config;
        }

        public async Task<AssistantResponse> CloneAssistantAsync(
            string sourceAssistantId, 
            string newName)
        {
            var client = _httpClientFactory.CreateClient("TelnyxClient");

            if (string.IsNullOrWhiteSpace(sourceAssistantId))
                throw new ArgumentException("Source assistant ID cannot be empty");
            if (string.IsNullOrWhiteSpace(newName))
                throw new ArgumentException("New assistant name cannot be empty");

            try
            {
                var response = await client.PostAsync(
                    $"/ai/assistants/{sourceAssistantId}/clone",
                    new StringContent(
                        JsonSerializer.Serialize(new { name = newName }),
                        System.Text.Encoding.UTF8,
                        "application/json"));

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    throw new HttpRequestException(
                        $"Telnyx API error: {response.StatusCode} - {errorContent}");
                }

                var content = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions 
                { 
                    PropertyNameCaseInsensitive = true,
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
                };
                var result = JsonSerializer.Deserialize<ApiResponse>(content, options);

                if (result?.Data == null)
                    throw new InvalidOperationException("Invalid response from Telnyx API");

                return result.Data;
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                throw new UnauthorizedAccessException("Invalid API key", ex);
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("429"))
            {
                throw new InvalidOperationException("Rate limit exceeded", ex);
            }
            catch (HttpRequestException ex)
            {
                throw new InvalidOperationException($"Network error: {ex.Message}", ex);
            }
        }
    }

    public class ApiResponse
    {
        [JsonPropertyName("data")]
        public AssistantResponse Data { get; set; }
    }

    public class AssistantResponse
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("model")]
        public string Model { get; set; }

        [JsonPropertyName("instructions")]
        public string Instructions { get; set; }

        [JsonPropertyName("enabled_features")]
        public List<string> EnabledFeatures { get; set; }

        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; }
    }
}

// ============================================================================

// Controllers/AssistantsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxAssistantCloner.Services;

namespace TelnyxAssistantCloner.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AssistantsController : ControllerBase
    {
        private readonly AssistantService _assistantService;
        private readonly ILogger<AssistantsController> _logger;

        public AssistantsController(
            AssistantService assistantService,
            ILogger<AssistantsController> logger)
        {
            _assistantService = assistantService;
            _logger = logger;
        }

        [HttpPost("{assistantId}/clone")]
        public async Task<IActionResult> CloneAssistant(
            string assistantId,
            [FromBody] CloneRequest request)
        {
            if (string.IsNullOrWhiteSpace(assistantId))
                return BadRequest(new { error = "Assistant ID is required" });

            if (request == null || string.IsNullOrWhiteSpace(request.Name))
                return BadRequest(new { error = "New assistant name is required" });

            try
            {
                var clonedAssistant = await _assistantService.CloneAssistantAsync(
                    assistantId,
                    request.Name);

                return Ok(new
                {
                    id = clonedAssistant.Id,
                    name = clonedAssistant.Name,
                    model = clonedAssistant.Model,
                    instructions = clonedAssistant.Instructions,
                    enabled_features = clonedAssistant.EnabledFeatures,
                    created_at = clonedAssistant.CreatedAt
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new { error = ex.Message });
            }
            catch (UnauthorizedAccessException ex)
            {
                _logger.LogError($"Authentication error: {ex.Message}");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Rate limit"))
            {
                _logger.LogWarning($"Rate limit: {ex.Message}");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (InvalidOperationException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }

    public class CloneRequest
    {
        public string Name { get; set; }
    }
}
