// Program.cs
using DotNetEnv;
using TelnyxWhisperPrompt.Services;

var builder = WebApplicationBuilder.CreateBuilder(args);

// Load environment variables from .env file
Env.Load();

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddHttpClient<CallControlService>();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseSession();
app.UseAuthorization();
app.MapControllers();

app.Run();

// ============================================================================

// Models/CallRequest.cs
namespace TelnyxWhisperPrompt.Models
{
    public class CallRequest
    {
        public string? Data { get; set; }
        public string? EventType { get; set; }
    }

    public class CallInitiateRequest
    {
        public string? To { get; set; }
        public string? WhisperMessage { get; set; }
    }

    public class CallResponse
    {
        public string? CallControlId { get; set; }
        public string? Status { get; set; }
    }
}

// ============================================================================

// Services/CallControlService.cs
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace TelnyxWhisperPrompt.Services
{
    public class CallControlService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _fromNumber;
        private readonly string _connectionId;
        private const string BaseUrl = "https://api.telnyx.com/v2";

        public CallControlService(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY") 
                ?? throw new InvalidOperationException("TELNYX_API_KEY not set");
            _fromNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER") 
                ?? throw new InvalidOperationException("TELNYX_PHONE_NUMBER not set");
            _connectionId = Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID") 
                ?? throw new InvalidOperationException("TELNYX_CONNECTION_ID not set");

            // Configure default headers for all requests
            _httpClient.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", _apiKey);
        }

        /// <summary>
        /// Initiate an outbound call with a whisper prompt.
        /// </summary>
        public async Task<Dictionary<string, object>> InitiateCallAsync(string toNumber)
        {
            if (string.IsNullOrEmpty(toNumber) || !toNumber.StartsWith("+"))
            {
                throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
            }

            var payload = new
            {
                from_ = _fromNumber,
                to = toNumber,
                connection_id = _connectionId,
                custom_headers = new[] 
                {
                    new { name = "X-Custom-Header", value = "whisper-prompt" }
                }
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync($"{BaseUrl}/calls", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to initiate call: {response.StatusCode} - {errorContent}"
                );
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            using var jsonDoc = JsonDocument.Parse(responseBody);
            var root = jsonDoc.RootElement;

            return new Dictionary<string, object>
            {
                { "call_control_id", root.GetProperty("data").GetProperty("call_control_id").GetString() ?? "" },
                { "status", "initiated" }
            };
        }

        /// <summary>
        /// Play a whisper message to the call recipient.
        /// </summary>
        public async Task PlayWhisperAsync(string callControlId, string message)
        {
            var payload = new
            {
                payload = message,
                language = "en-US",
                voice = "female"
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                $"{BaseUrl}/calls/{callControlId}/actions/speak",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to play whisper: {response.StatusCode} - {errorContent}"
                );
            }
        }

        /// <summary>
        /// Transfer the call to the original caller.
        /// </summary>
        public async Task TransferCallAsync(string callControlId, string transferTo)
        {
            var payload = new
            {
                to = transferTo
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                $"{BaseUrl}/calls/{callControlId}/actions/transfer",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to transfer call: {response.StatusCode} - {errorContent}"
                );
            }
        }

        /// <summary>
        /// Hang up a call.
        /// </summary>
        public async Task HangupCallAsync(string callControlId)
        {
            var payload = new { };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                $"{BaseUrl}/calls/{callControlId}/actions/hangup",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to hangup call: {response.StatusCode} - {errorContent}"
                );
            }
        }
    }
}

// ============================================================================

// Controllers/CallsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxWhisperPrompt.Models;
using TelnyxWhisperPrompt.Services;

namespace TelnyxWhisperPrompt.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CallsController : ControllerBase
    {
        private readonly CallControlService _callControlService;
        private readonly ILogger<CallsController> _logger;

        public CallsController(CallControlService callControlService, ILogger<CallsController> logger)
        {
            _callControlService = callControlService;
            _logger = logger;
        }

        /// <summary>
        /// Initiate an outbound call with a whisper prompt.
        /// POST /api/calls/initiate
        /// </summary>
        [HttpPost("initiate")]
        public async Task<IActionResult> InitiateCall([FromBody] CallInitiateRequest request)
        {
            if (request == null || string.IsNullOrEmpty(request.To))
            {
                return BadRequest(new { error = "Missing required field: 'to'" });
            }

            if (string.IsNullOrEmpty(request.WhisperMessage))
            {
                return BadRequest(new { error = "Missing required field: 'whisperMessage'" });
            }

            try
            {
                var result = await _callControlService.InitiateCallAsync(request.To);
                
                // Store whisper message and transfer number in session/cache for webhook handling
                // In production, use a database or distributed cache
                HttpContext.Session.SetString(
                    $"whisper_{result["call_control_id"]}", 
                    request.WhisperMessage
                );

                return Ok(new
                {
                    call_control_id = result["call_control_id"],
                    status = result["status"],
                    message = "Call initiated. Whisper prompt will play when recipient answers."
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogWarning($"Validation error: {ex.Message}");
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(503, new { error = "Failed to initiate call. Please try again." });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// Webhook endpoint to receive call events from Telnyx.
        /// POST /api/calls/webhook
        /// </summary>
        [HttpPost("webhook")]
        public async Task<IActionResult> HandleWebhook([FromBody] JsonElement payload)
        {
            try
            {
                var eventType = payload.GetProperty("data").GetProperty("event_type").GetString();
                var callControlId = payload.GetProperty("data").GetProperty("call_control_id").GetString();

                _logger.LogInformation($"Received webhook event: {eventType} for call {callControlId}");

                switch (eventType)
                {
                    case "call.answered":
                        await HandleCallAnswered(callControlId);
                        break;

                    case "call.speak.ended":
                        await HandleSpeakEnded(callControlId);
                        break;

                    case "call.hangup":
                        _logger.LogInformation($"Call {callControlId} ended");
                        break;

                    default:
                        _logger.LogInformation($"Unhandled event type: {eventType}");
                        break;
                }

                return Ok(new { status = "received" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Webhook processing error: {ex.Message}");
                return StatusCode(500, new { error = "Webhook processing failed" });
            }
        }

        /// <summary>
        /// Handle call.answered event: play whisper prompt.
        /// </summary>
        private async Task HandleCallAnswered(string callControlId)
        {
            try
            {
                // In production, retrieve whisper message from database/cache
                var whisperMessage = "Hello, you have an incoming call. Please wait while we connect you.";
                
                await _callControlService.PlayWhisperAsync(callControlId, whisperMessage);
                _logger.LogInformation($"Whisper prompt played for call {callControlId}");
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error playing whisper: {ex.Message}");
            }
        }

        /// <summary>
        /// Handle call.speak.ended event: transfer call to original caller.
        /// </summary>
        private async Task HandleSpeakEnded(string callControlId)
        {
            try
            {
                // In production, retrieve transfer number from database/cache
                var transferTo = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER") 
                    ?? throw new InvalidOperationException("TELNYX_PHONE_NUMBER not set");
                
                await _callControlService.TransferCallAsync(callControlId, transferTo);
                _logger.LogInformation($"Call {callControlId} transferred to {transferTo}");
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error transferring call: {ex.Message}");
            }
        }
    }
}
