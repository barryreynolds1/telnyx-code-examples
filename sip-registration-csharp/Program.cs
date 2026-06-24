// Program.cs
using TelnyxSipRegistration.Services;

DotNetEnv.Env.Load();

var builder = WebApplicationBuilder.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddHttpClient<TelnyxSipService>();
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

// Models/SipConnectionRequest.cs
namespace TelnyxSipRegistration.Models
{
    public class SipConnectionRequest
    {
        public string Name { get; set; }
        public string Username { get; set; }
        public string Password { get; set; }
        public List<string> SipUris { get; set; }
        public string OutboundVoiceProfileId { get; set; }
    }
}

// Models/SipConnectionResponse.cs
namespace TelnyxSipRegistration.Models
{
    public class SipConnectionResponse
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Username { get; set; }
        public List<string> SipUris { get; set; }
        public string Status { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}

// Services/TelnyxSipService.cs
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using TelnyxSipRegistration.Models;

namespace TelnyxSipRegistration.Services
{
    public class TelnyxSipService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _apiBaseUrl;

        public TelnyxSipService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY") 
                ?? configuration["Telnyx:ApiKey"];
            _apiBaseUrl = Environment.GetEnvironmentVariable("TELNYX_API_BASE_URL") 
                ?? configuration["Telnyx:ApiBaseUrl"];

            if (string.IsNullOrEmpty(_apiKey))
                throw new InvalidOperationException("TELNYX_API_KEY environment variable not set");
        }

        public async Task<SipConnectionResponse> CreateSipConnectionAsync(SipConnectionRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Name))
                throw new ArgumentException("SIP connection name is required");
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
                    outbound_voice_profile_id = request.OutboundVoiceProfileId
                }
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var request_msg = new HttpRequestMessage(HttpMethod.Post, $"{_apiBaseUrl}/sip_connections")
            {
                Content = content
            };

            request_msg.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);

            var response = await _httpClient.SendAsync(request_msg);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Telnyx API error: {response.StatusCode} - {errorContent}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            var jsonDoc = JsonDocument.Parse(responseContent);
            var dataElement = jsonDoc.RootElement.GetProperty("data");

            return new SipConnectionResponse
            {
                Id = dataElement.GetProperty("id").GetString(),
                Name = dataElement.GetProperty("name").GetString(),
                Username = dataElement.GetProperty("username").GetString(),
                SipUris = dataElement.GetProperty("sip_uris")
                    .EnumerateArray()
                    .Select(x => x.GetString())
                    .ToList(),
                Status = dataElement.GetProperty("status").GetString(),
                CreatedAt = DateTime.Parse(dataElement.GetProperty("created_at").GetString())
            };
        }

        public async Task<SipConnectionResponse> GetSipConnectionAsync(string connectionId)
        {
            if (string.IsNullOrWhiteSpace(connectionId))
                throw new ArgumentException("Connection ID is required");

            var request = new HttpRequestMessage(HttpMethod.Get, $"{_apiBaseUrl}/sip_connections/{connectionId}");
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);

            var response = await _httpClient.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Telnyx API error: {response.StatusCode} - {errorContent}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            var jsonDoc = JsonDocument.Parse(responseContent);
            var dataElement = jsonDoc.RootElement.GetProperty("data");

            return new SipConnectionResponse
            {
                Id = dataElement.GetProperty("id").GetString(),
                Name = dataElement.GetProperty("name").GetString(),
                Username = dataElement.GetProperty("username").GetString(),
                SipUris = dataElement.GetProperty("sip_uris")
                    .EnumerateArray()
                    .Select(x => x.GetString())
                    .ToList(),
                Status = dataElement.GetProperty("status").GetString(),
                CreatedAt = DateTime.Parse(dataElement.GetProperty("created_at").GetString())
            };
        }
    }
}

// Controllers/SipConnectionsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSipRegistration.Models;
using TelnyxSipRegistration.Services;

namespace TelnyxSipRegistration.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SipConnectionsController : ControllerBase
    {
        private readonly TelnyxSipService _sipService;
        private readonly ILogger<SipConnectionsController> _logger;

        public SipConnectionsController(TelnyxSipService sipService, ILogger<SipConnectionsController> logger)
        {
            _sipService = sipService;
            _logger = logger;
        }

        [HttpPost("register")]
        public async Task<IActionResult> RegisterSipConnection([FromBody] SipConnectionRequest request)
        {
            if (!ModelState.IsValid)
                return BadRequest(new { error = "Invalid request body" });

            try
            {
                var result = await _sipService.CreateSipConnectionAsync(request);
                return Ok(new
                {
                    id = result.Id,
                    name = result.Name,
                    username = result.Username,
                    sip_uris = result.SipUris,
                    status = result.Status,
                    created_at = result.CreatedAt
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("429"))
            {
                _logger.LogWarning("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Telnyx API error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet("{connectionId}")]
        public async Task<IActionResult> GetSipConnection(string connectionId)
        {
            if (string.IsNullOrWhiteSpace(connectionId))
                return BadRequest(new { error = "Connection ID is required" });

            try
            {
                var result = await _sipService.GetSipConnectionAsync(connectionId);
                return Ok(new
                {
                    id = result.Id,
                    name = result.Name,
                    username = result.Username,
                    sip_uris = result.SipUris,
                    status = result.Status,
                    created_at = result.CreatedAt
                });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("404"))
            {
                return NotFound(new { error = "SIP connection not found" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Telnyx API error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}
