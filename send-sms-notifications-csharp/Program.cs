// Program.cs
using DotNetEnv;
using Microsoft.Extensions.Options;
using TelnyxSmsNotifications.Configuration;
using TelnyxSmsNotifications.Services;

// Load environment variables from .env file
Env.Load();

var builder = WebApplicationBuilder.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register Telnyx configuration
builder.Services.Configure<TelnyxConfig>(config =>
{
    config.ApiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY") 
        ?? throw new InvalidOperationException("TELNYX_API_KEY not set");
    config.PhoneNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER") 
        ?? throw new InvalidOperationException("TELNYX_PHONE_NUMBER not set");
});

// Register HTTP client for Telnyx API
builder.Services.AddHttpClient("TelnyxClient", (serviceProvider, client) =>
{
    var config = serviceProvider.GetRequiredService<IOptions<TelnyxConfig>>();
    client.BaseAddress = new Uri("https://api.telnyx.com/v2/");
    client.DefaultRequestHeaders.Authorization = 
        new System.Net.Http.Headers.AuthenticationHeaderValue(
            "Bearer", config.Value.ApiKey);
});

// Register SMS notification service
builder.Services.AddScoped<ISmsNotificationService, SmsNotificationService>();

var app = builder.Build();

// Configure the HTTP request pipeline
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
namespace TelnyxSmsNotifications.Configuration
{
    public class TelnyxConfig
    {
        public string ApiKey { get; set; }
        public string PhoneNumber { get; set; }
    }
}

// ============================================================================
// Services/ISmsNotificationService.cs
namespace TelnyxSmsNotifications.Services
{
    public interface ISmsNotificationService
    {
        Task<SmsNotificationResponse> SendNotificationAsync(string toNumber, string message);
    }

    public class SmsNotificationResponse
    {
        public string MessageId { get; set; }
        public string Status { get; set; }
        public string From { get; set; }
        public string To { get; set; }
    }
}

// ============================================================================
// Services/SmsNotificationService.cs
using Microsoft.Extensions.Options;
using System.Text;
using System.Text.Json;
using TelnyxSmsNotifications.Configuration;

namespace TelnyxSmsNotifications.Services
{
    public class SmsNotificationService : ISmsNotificationService
    {
        private readonly HttpClient _httpClient;
        private readonly TelnyxConfig _config;
        private readonly ILogger<SmsNotificationService> _logger;

        public SmsNotificationService(
            IHttpClientFactory httpClientFactory,
            IOptions<TelnyxConfig> config,
            ILogger<SmsNotificationService> logger)
        {
            _httpClient = httpClientFactory.CreateClient("TelnyxClient");
            _config = config.Value;
            _logger = logger;
        }

        public async Task<SmsNotificationResponse> SendNotificationAsync(string toNumber, string message)
        {
            // Validate E.164 format to prevent API errors
            if (string.IsNullOrWhiteSpace(toNumber) || !toNumber.StartsWith("+"))
            {
                throw new ArgumentException(
                    "Phone number must be in E.164 format (e.g., +15551234567)", 
                    nameof(toNumber));
            }

            if (string.IsNullOrWhiteSpace(message))
            {
                throw new ArgumentException("Message cannot be empty", nameof(message));
            }

            // Prepare request payload
            var payload = new
            {
                from_ = _config.PhoneNumber,
                to = toNumber,
                text = message
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            try
            {
                _logger.LogInformation(
                    "Sending SMS notification to {ToNumber} from {FromNumber}",
                    toNumber, _config.PhoneNumber);

                var response = await _httpClient.PostAsync("messages", jsonContent);

                // Handle HTTP errors
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError(
                        "Telnyx API error: {StatusCode} - {ErrorContent}",
                        response.StatusCode, errorContent);

                    throw new HttpRequestException(
                        $"Telnyx API returned {response.StatusCode}: {errorContent}",
                        null,
                        response.StatusCode);
                }

                // Parse successful response
                var responseContent = await response.Content.ReadAsStringAsync();
                using var jsonDoc = JsonDocument.Parse(responseContent);
                var root = jsonDoc.RootElement;

                // Extract message ID and status from nested response structure
                var messageId = root.GetProperty("data").GetProperty("id").GetString();
                var toArray = root.GetProperty("data").GetProperty("to");
                var status = toArray.EnumerateArray().FirstOrDefault()
                    .GetProperty("status").GetString() ?? "queued";

                _logger.LogInformation(
                    "SMS notification sent successfully. Message ID: {MessageId}",
                    messageId);

                return new SmsNotificationResponse
                {
                    MessageId = messageId,
                    Status = status,
                    From = _config.PhoneNumber,
                    To = toNumber
                };
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                throw new InvalidOperationException("Invalid Telnyx API key", ex);
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                throw new InvalidOperationException("Rate limit exceeded. Please slow down.", ex);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError("Network error: {Message}", ex.Message);
                throw new InvalidOperationException("Network error connecting to Telnyx", ex);
            }
        }
    }
}

// ============================================================================
// Controllers/SmsNotificationController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSmsNotifications.Services;

namespace TelnyxSmsNotifications.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SmsNotificationController : ControllerBase
    {
        private readonly ISmsNotificationService _smsService;
        private readonly ILogger<SmsNotificationController> _logger;

        public SmsNotificationController(
            ISmsNotificationService smsService,
            ILogger<SmsNotificationController> logger)
        {
            _smsService = smsService;
            _logger = logger;
        }

        [HttpPost("send")]
        public async Task<IActionResult> SendNotification([FromBody] SendNotificationRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.To) || string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(new { error = "Missing required fields: 'to' and 'message'" });
            }

            try
            {
                var result = await _smsService.SendNotificationAsync(request.To, request.Message);
                return Ok(new
                {
                    message_id = result.MessageId,
                    status = result.Status,
                    from = result.From,
                    to = result.To
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning("Validation error: {Message}", ex.Message);
                return BadRequest(new { error = ex.Message });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Invalid Telnyx API key"))
            {
                _logger.LogError("Authentication error: {Message}", ex.Message);
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Rate limit"))
            {
                _logger.LogError("Rate limit error: {Message}", ex.Message);
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Network error"))
            {
                _logger.LogError("Network error: {Message}", ex.Message);
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError("Unexpected error: {Message}", ex.Message);
                return StatusCode(500, new { error = "An unexpected error occurred" });
            }
        }
    }

    public class SendNotificationRequest
    {
        public string To { get; set; }
        public string Message { get; set; }
    }
}
