using DotNetEnv;
using Microsoft.AspNetCore.Mvc;
using System.Net.Http.Headers;
using System.Text.Json;

var builder = WebApplicationBuilder.CreateBuilder(args);

// Load environment variables from .env file
DotNetEnv.Env.Load();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

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

namespace TelnyxSimActivation.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SimCardController : ControllerBase
    {
        private readonly ILogger<SimCardController> _logger;
        private readonly HttpClient _httpClient;

        public SimCardController(ILogger<SimCardController> logger)
        {
            _logger = logger;
            _httpClient = new HttpClient();
            
            // Configure HTTP client with Telnyx API base URL and authentication
            _httpClient.BaseAddress = new Uri("https://api.telnyx.com/v2/");
            var apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY");
            if (string.IsNullOrEmpty(apiKey))
            {
                throw new InvalidOperationException("TELNYX_API_KEY environment variable not set");
            }
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", apiKey);
            _httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        /// <summary>
        /// Activate a SIM card by ID.
        /// </summary>
        [HttpPost("activate")]
        public async Task<IActionResult> ActivateSimCard([FromBody] ActivateSimRequest request)
        {
            // Validate request payload
            if (string.IsNullOrWhiteSpace(request?.SimCardId))
            {
                return BadRequest(new { error = "Missing required field: 'sim_card_id'" });
            }

            try
            {
                // Build request payload for Telnyx API
                var payload = new
                {
                    activation_settings = new
                    {
                        apn = request.Apn ?? "internet.telnyx"
                    }
                };

                var jsonContent = new StringContent(
                    JsonSerializer.Serialize(payload),
                    System.Text.Encoding.UTF8,
                    "application/json");

                // Send activation request to Telnyx API
                var response = await _httpClient.PostAsync(
                    $"sim_cards/{request.SimCardId}/actions/activate",
                    jsonContent);

                // Handle API response
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return HandleApiError(response.StatusCode, responseContent);
                }

                // Parse and extract serializable response data
                using (JsonDocument doc = JsonDocument.Parse(responseContent))
                {
                    var root = doc.RootElement;
                    if (root.TryGetProperty("data", out var dataElement))
                    {
                        var simData = dataElement;
                        return Ok(new
                        {
                            id = simData.GetProperty("id").GetString(),
                            iccid = simData.GetProperty("iccid").GetString(),
                            status = simData.GetProperty("status").GetString(),
                            sim_card_group_id = simData.TryGetProperty("sim_card_group_id", out var groupId) 
                                ? groupId.GetString() 
                                : null,
                            message = "SIM card activation initiated"
                        });
                    }
                }

                return Ok(new { message = "SIM card activation initiated" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// Get SIM card details by ID.
        /// </summary>
        [HttpGet("{simCardId}")]
        public async Task<IActionResult> GetSimCard(string simCardId)
        {
            if (string.IsNullOrWhiteSpace(simCardId))
            {
                return BadRequest(new { error = "SIM card ID is required" });
            }

            try
            {
                var response = await _httpClient.GetAsync($"sim_cards/{simCardId}");
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return HandleApiError(response.StatusCode, responseContent);
                }

                // Parse and extract serializable response data
                using (JsonDocument doc = JsonDocument.Parse(responseContent))
                {
                    var root = doc.RootElement;
                    if (root.TryGetProperty("data", out var dataElement))
                    {
                        var simData = dataElement;
                        return Ok(new
                        {
                            id = simData.GetProperty("id").GetString(),
                            iccid = simData.GetProperty("iccid").GetString(),
                            status = simData.GetProperty("status").GetString(),
                            sim_card_group_id = simData.TryGetProperty("sim_card_group_id", out var groupId) 
                                ? groupId.GetString() 
                                : null
                        });
                    }
                }

                return Ok(new { message = "SIM card retrieved" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// Handle Telnyx API errors and map to appropriate HTTP status codes.
        /// </summary>
        private IActionResult HandleApiError(System.Net.HttpStatusCode statusCode, string responseContent)
        {
            return statusCode switch
            {
                System.Net.HttpStatusCode.Unauthorized => 
                    Unauthorized(new { error = "Invalid API key" }),
                System.Net.HttpStatusCode.TooManyRequests => 
                    StatusCode(429, new { error = "Rate limit exceeded. Please slow down." }),
                System.Net.HttpStatusCode.NotFound => 
                    NotFound(new { error = "SIM card not found" }),
                System.Net.HttpStatusCode.BadRequest => 
                    BadRequest(new { error = "Invalid request parameters", details = responseContent }),
                _ => 
                    StatusCode((int)statusCode, new { error = "Telnyx API error", details = responseContent })
            };
        }
    }

    /// <summary>
    /// Request model for SIM card activation.
    /// </summary>
    public class ActivateSimRequest
    {
        public string SimCardId { get; set; }
        public string Apn { get; set; }
    }
}
