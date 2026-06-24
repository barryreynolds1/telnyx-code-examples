// Program.cs
using DotNetEnv;
using TelnyxNumberLookup.Services;

var builder = WebApplication.CreateBuilder(args);

Env.Load();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddScoped<INumberLookupService, NumberLookupService>();

builder.Services.AddHttpClient<INumberLookupService, NumberLookupService>(client =>
{
    client.BaseAddress = new Uri("https://api.telnyx.com/v2/");
    var apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY");
    client.DefaultRequestHeaders.Authorization =
        new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);
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

// Models/NumberLookupResponse.cs
namespace TelnyxNumberLookup.Models
{
    public class NumberLookupResponse
    {
        public string PhoneNumber { get; set; }
        public string CountryCode { get; set; }
        public string Carrier { get; set; }
        public string LineType { get; set; }
        public string City { get; set; }
        public string State { get; set; }
        public bool IsValid { get; set; }
        public string LookupId { get; set; }
    }

    public class LookupRequest
    {
        public string PhoneNumber { get; set; }
    }

    public class ErrorResponse
    {
        public string Error { get; set; }
        public int? StatusCode { get; set; }
    }
}

// Services/INumberLookupService.cs
namespace TelnyxNumberLookup.Services
{
    public interface INumberLookupService
    {
        Task<Models.NumberLookupResponse> LookupPhoneNumberAsync(string phoneNumber);
    }
}

// Services/NumberLookupService.cs
using System.Text.Json;
using TelnyxNumberLookup.Models;

namespace TelnyxNumberLookup.Services
{
    public class NumberLookupService : INumberLookupService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<NumberLookupService> _logger;

        public NumberLookupService(HttpClient httpClient, ILogger<NumberLookupService> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        public async Task<NumberLookupResponse> LookupPhoneNumberAsync(string phoneNumber)
        {
            if (string.IsNullOrWhiteSpace(phoneNumber) || !phoneNumber.StartsWith("+"))
            {
                throw new ArgumentException(
                    "Phone number must be in E.164 format (e.g., +15551234567)");
            }

            try
            {
                var response = await _httpClient.GetAsync($"number_lookup?phone_number={Uri.EscapeDataString(phoneNumber)}");

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError($"Telnyx API error: {response.StatusCode} - {errorContent}");

                    if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                    {
                        throw new UnauthorizedAccessException("Invalid API key");
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                    {
                        throw new InvalidOperationException("Rate limit exceeded. Please slow down.");
                    }
                    else
                    {
                        throw new HttpRequestException(
                            $"Telnyx API returned {response.StatusCode}: {errorContent}");
                    }
                }

                var content = await response.Content.ReadAsStringAsync();
                var jsonDoc = JsonDocument.Parse(content);
                var data = jsonDoc.RootElement.GetProperty("data");

                return new NumberLookupResponse
                {
                    PhoneNumber = phoneNumber,
                    CountryCode = data.TryGetProperty("country_code", out var cc) 
                        ? cc.GetString() : "Unknown",
                    Carrier = data.TryGetProperty("carrier_name", out var cn) 
                        ? cn.GetString() : "Unknown",
                    LineType = data.TryGetProperty("line_type", out var lt) 
                        ? lt.GetString() : "Unknown",
                    City = data.TryGetProperty("city", out var city) 
                        ? city.GetString() : "Unknown",
                    State = data.TryGetProperty("state", out var state) 
                        ? state.GetString() : "Unknown",
                    IsValid = data.TryGetProperty("phone_number_valid", out var valid) 
                        ? valid.GetBoolean() : false,
                    LookupId = data.TryGetProperty("id", out var id) 
                        ? id.GetString() : "Unknown"
                };
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                throw new InvalidOperationException("Network error connecting to Telnyx", ex);
            }
        }
    }
}

// Controllers/NumberLookupController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxNumberLookup.Models;
using TelnyxNumberLookup.Services;

namespace TelnyxNumberLookup.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class NumberLookupController : ControllerBase
    {
        private readonly INumberLookupService _lookupService;
        private readonly ILogger<NumberLookupController> _logger;

        public NumberLookupController(
            INumberLookupService lookupService,
            ILogger<NumberLookupController> logger)
        {
            _lookupService = lookupService;
            _logger = logger;
        }

        [HttpPost("lookup")]
        public async Task<ActionResult<NumberLookupResponse>> LookupNumber(
            [FromBody] LookupRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.PhoneNumber))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "Missing required field: 'phoneNumber'"
                });
            }

            try
            {
                var result = await _lookupService.LookupPhoneNumberAsync(request.PhoneNumber);
                return Ok(result);
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new ErrorResponse { Error = ex.Message });
            }
            catch (UnauthorizedAccessException ex)
            {
                _logger.LogError($"Authentication error: {ex.Message}");
                return Unauthorized(new ErrorResponse
                {
                    Error = "Invalid API key",
                    StatusCode = 401
                });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Rate limit"))
            {
                _logger.LogWarning($"Rate limit: {ex.Message}");
                return StatusCode(429, new ErrorResponse
                {
                    Error = ex.Message,
                    StatusCode = 429
                });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Network error"))
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new ErrorResponse
                {
                    Error = "Network error connecting to Telnyx",
                    StatusCode = 503
                });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new ErrorResponse
                {
                    Error = "An unexpected error occurred",
                    StatusCode = 500
                });
            }
        }
    }
}
