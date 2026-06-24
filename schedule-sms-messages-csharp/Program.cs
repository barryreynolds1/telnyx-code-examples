// Program.cs
using Hangfire;
using Hangfire.InMemory;
using TelnyxScheduledSms.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddHangfire(config =>
    config.UseInMemoryStorage()
);
builder.Services.AddHangfireServer();

builder.Services.AddHttpClient<ITelnyxSmsService, TelnyxSmsService>();
builder.Services.AddScoped<IScheduledSmsService, ScheduledSmsService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.UseHangfireDashboard();

app.MapControllers();

app.Run();

// Models/ScheduledSmsRequest.cs
using System;

namespace TelnyxScheduledSms.Models
{
    public class ScheduledSmsRequest
    {
        public string To { get; set; }
        public string Message { get; set; }
        public DateTime ScheduledTime { get; set; }
    }

    public class SmsResponse
    {
        public string MessageId { get; set; }
        public string Status { get; set; }
        public string From { get; set; }
        public string To { get; set; }
        public DateTime ScheduledTime { get; set; }
    }
}

// Services/TelnyxSmsService.cs
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace TelnyxScheduledSms.Services
{
    public interface ITelnyxSmsService
    {
        Task<SmsResponse> SendSmsAsync(string toNumber, string message);
    }

    public class SmsResponse
    {
        public string MessageId { get; set; }
        public string Status { get; set; }
        public string From { get; set; }
        public string To { get; set; }
    }

    public class TelnyxSmsService : ITelnyxSmsService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<TelnyxSmsService> _logger;
        private const string TelnyxApiUrl = "https://api.telnyx.com/v2/messages";

        public TelnyxSmsService(HttpClient httpClient, IConfiguration configuration, ILogger<TelnyxSmsService> logger)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<SmsResponse> SendSmsAsync(string toNumber, string message)
        {
            if (string.IsNullOrEmpty(toNumber) || !toNumber.StartsWith("+"))
            {
                throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
            }

            var fromNumber = _configuration["Telnyx:PhoneNumber"];
            if (string.IsNullOrEmpty(fromNumber))
            {
                throw new InvalidOperationException("Telnyx:PhoneNumber configuration not set");
            }

            var apiKey = _configuration["Telnyx:ApiKey"];
            if (string.IsNullOrEmpty(apiKey))
            {
                throw new InvalidOperationException("Telnyx:ApiKey configuration not set");
            }

            var requestBody = new
            {
                from_ = fromNumber,
                to = toNumber,
                text = message
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestBody),
                Encoding.UTF8,
                "application/json"
            );

            _httpClient.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);

            try
            {
                var response = await _httpClient.PostAsync(TelnyxApiUrl, jsonContent);

                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var jsonDoc = JsonDocument.Parse(responseContent);
                    var data = jsonDoc.RootElement.GetProperty("data");

                    return new SmsResponse
                    {
                        MessageId = data.GetProperty("id").GetString(),
                        Status = data.GetProperty("to")[0].GetProperty("status").GetString(),
                        From = fromNumber,
                        To = toNumber
                    };
                }

                if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                {
                    throw new UnauthorizedAccessException("Invalid Telnyx API key");
                }

                if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                {
                    throw new InvalidOperationException("Rate limit exceeded. Please slow down.");
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError($"Telnyx API error: {response.StatusCode} - {errorContent}");
                throw new InvalidOperationException($"Telnyx API error: {response.StatusCode}");
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error connecting to Telnyx: {ex.Message}");
                throw new InvalidOperationException("Network error connecting to Telnyx", ex);
            }
        }
    }
}

// Services/ScheduledSmsService.cs
using System;
using System.Threading.Tasks;
using Hangfire;
using Microsoft.Extensions.Logging;
using TelnyxScheduledSms.Models;

namespace TelnyxScheduledSms.Services
{
    public interface IScheduledSmsService
    {
        string ScheduleSms(string toNumber, string message, DateTime scheduledTime);
        Task<SmsResponse> SendSmsAsync(string toNumber, string message);
    }

    public class ScheduledSmsService : IScheduledSmsService
    {
        private readonly ITelnyxSmsService _telnyxService;
        private readonly ILogger<ScheduledSmsService> _logger;

        public ScheduledSmsService(ITelnyxSmsService telnyxService, ILogger<ScheduledSmsService> logger)
        {
            _telnyxService = telnyxService;
            _logger = logger;
        }

        public string ScheduleSms(string toNumber, string message, DateTime scheduledTime)
        {
            if (scheduledTime <= DateTime.UtcNow)
            {
                throw new ArgumentException("Scheduled time must be in the future");
            }

            var jobId = BackgroundJob.Schedule(
                () => SendSmsAsync(toNumber, message),
                scheduledTime
            );

            _logger.LogInformation($"SMS scheduled with job ID: {jobId} for {scheduledTime:O}");
            return jobId;
        }

        public async Task<SmsResponse> SendSmsAsync(string toNumber, string message)
        {
            _logger.LogInformation($"Executing scheduled SMS to {toNumber}");
            return await _telnyxService.SendSmsAsync(toNumber, message);
        }
    }
}

// Controllers/SmsController.cs
using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using TelnyxScheduledSms.Models;
using TelnyxScheduledSms.Services;

namespace TelnyxScheduledSms.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SmsController : ControllerBase
    {
        private readonly IScheduledSmsService _scheduledSmsService;
        private readonly ILogger<SmsController> _logger;

        public SmsController(IScheduledSmsService scheduledSmsService, ILogger<SmsController> logger)
        {
            _scheduledSmsService = scheduledSmsService;
            _logger = logger;
        }

        [HttpPost("schedule")]
        public IActionResult ScheduleSms([FromBody] ScheduledSmsRequest request)
        {
            if (request == null)
            {
                return BadRequest(new { error = "Request body required" });
            }

            if (string.IsNullOrEmpty(request.To) || string.IsNullOrEmpty(request.Message))
            {
                return BadRequest(new { error = "Missing required fields: 'to' and 'message'" });
            }

            try
            {
                var jobId = _scheduledSmsService.ScheduleSms(request.To, request.Message, request.ScheduledTime);

                return Accepted(new
                {
                    jobId = jobId,
                    to = request.To,
                    message = request.Message,
                    scheduledTime = request.ScheduledTime,
                    status = "scheduled"
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new { error = ex.Message });
            }
            catch (InvalidOperationException ex)
            {
                _logger.LogError($"Configuration error: {ex.Message}");
                return StatusCode(500, new { error = "Server configuration error" });
            }
        }

        [HttpPost("send")]
        public async Task<IActionResult> SendSmsNow([FromBody] ScheduledSmsRequest request)
        {
            if (request == null)
            {
                return BadRequest(new { error = "Request body required" });
            }

            if (string.IsNullOrEmpty(request.To) || string.IsNullOrEmpty(request.Message))
            {
                return BadRequest(new { error = "Missing required fields: 'to' and 'message'" });
            }

            try
            {
                var result = await _scheduledSmsService.SendSmsAsync(request.To, request.Message);

                return Ok(new
                {
                    messageId = result.MessageId,
                    status = result.Status,
                    from = result.From,
                    to = result.To
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new { error = ex.Message });
            }
            catch (UnauthorizedAccessException)
            {
                _logger.LogError("Authentication failed with Telnyx API");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Rate limit"))
            {
                _logger.LogWarning("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Network error"))
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (InvalidOperationException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
