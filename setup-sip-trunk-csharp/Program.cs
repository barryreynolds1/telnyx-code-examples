// Program.cs
using TelnyxSipTrunking.Services;

var builder = WebApplication.CreateBuilder(args);

// Load environment variables from .env file
var apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY");
var apiBaseUrl = Environment.GetEnvironmentVariable("TELNYX_API_BASE_URL") 
    ?? "https://api.telnyx.com/v2";

if (string.IsNullOrEmpty(apiKey))
{
    throw new InvalidOperationException("TELNYX_API_KEY environment variable is not set");
}

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure HttpClient with Telnyx API base URL and Bearer token
builder.Services.AddHttpClient<SipConnectionService>(client =>
{
    client.BaseAddress = new Uri(apiBaseUrl);
    client.DefaultRequestHeaders.Authorization = 
        new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);
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

// Models/SipConnectionRequest.cs
namespace TelnyxSipTrunking.Models
{
    public class SipConnectionRequest
    {
        public string Name { get; set; }
        public string Username { get; set; }
        public string Password { get; set; }
        public List<string> SipUris { get; set; }
        public string ConnectionType { get; set; } = "credential";
    }

    public class SipConnectionResponse
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Username { get; set; }
        public string ConnectionType { get; set; }
        public List<string> SipUris { get; set; }
        public string CreatedAt { get; set; }
    }

    public class SipConnectionListResponse
    {
        public List<SipConnectionResponse> Data { get; set; }
    }
}

// Services/SipConnectionService.cs
using System.Text;
using System.Text.Json;
using TelnyxSipTrunking.Models;

namespace TelnyxSipTrunking.Services
{
    public class SipConnectionService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<SipConnectionService> _logger;

        public SipConnectionService(HttpClient httpClient, ILogger<SipConnectionService> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        public async Task<List<SipConnectionResponse>> ListConnectionsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/sip_connections");
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<SipConnectionListResponse>(content, options);

                return result?.Data ?? new List<SipConnectionResponse>();
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error listing SIP connections: {ex.Message}");
                throw;
            }
        }

        public async Task<SipConnectionResponse> CreateConnectionAsync(SipConnectionRequest request)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(request.Name))
                    throw new ArgumentException("Connection name is required");
                if (string.IsNullOrWhiteSpace(request.Username))
                    throw new ArgumentException("Username is required");
                if (string.IsNullOrWhiteSpace(request.Password))
                    throw new ArgumentException("Password is required");
                if (request.SipUris == null || request.SipUris.Count == 0)
                    throw new ArgumentException("At least one SIP URI is required");

                var payload = new
                {
                    data = new
                    {
                        name = request.Name,
                        username = request.Username,
                        password = request.Password,
                        sip_uris = request.SipUris,
                        connection_type = request.ConnectionType
                    }
                };

                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/sip_connections", content);
                response.EnsureSuccessStatusCode();

                var responseContent = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<dynamic>(responseContent, options);

                var connectionData = JsonSerializer.Deserialize<SipConnectionResponse>(
                    JsonSerializer.Serialize(result), options);

                return connectionData;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error creating SIP connection: {ex.Message}");
                throw;
            }
        }

        public async Task<SipConnectionResponse> GetConnectionAsync(string connectionId)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(connectionId))
                    throw new ArgumentException("Connection ID is required");

                var response = await _httpClient.GetAsync($"/sip_connections/{connectionId}");
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<dynamic>(content, options);

                var connectionData = JsonSerializer.Deserialize<SipConnectionResponse>(
                    JsonSerializer.Serialize(result), options);

                return connectionData;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error retrieving SIP connection: {ex.Message}");
                throw;
            }
        }
    }
}

// Controllers/SipConnectionsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSipTrunking.Models;
using TelnyxSipTrunking.Services;

namespace TelnyxSipTrunking.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SipConnectionsController : ControllerBase
    {
        private readonly SipConnectionService _sipService;
        private readonly ILogger<SipConnectionsController> _logger;

        public SipConnectionsController(SipConnectionService sipService, ILogger<SipConnectionsController> logger)
        {
            _sipService = sipService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> ListConnections()
        {
            try
            {
                var connections = await _sipService.ListConnectionsAsync();
                return Ok(new { data = connections });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
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

        [HttpPost]
        public async Task<IActionResult> CreateConnection([FromBody] SipConnectionRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { error = "Invalid request body" });
            }

            try
            {
                var connection = await _sipService.CreateConnectionAsync(request);
                return CreatedAtAction(nameof(GetConnection), new { id = connection.Id }, connection);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error: {ex.Message}");
                return StatusCode(500, new { error = "Failed to create SIP connection" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetConnection(string id)
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return BadRequest(new { error = "Connection ID is required" });
            }

            try
            {
                var connection = await _sipService.GetConnectionAsync(id);
                return Ok(connection);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                return NotFound(new { error = "SIP connection not found" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error: {ex.Message}");
                return StatusCode(500, new { error = "Failed to retrieve SIP connection" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}
