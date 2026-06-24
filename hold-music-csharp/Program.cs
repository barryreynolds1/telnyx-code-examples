// Program.cs
using TelnyxHoldMusic.Services;

var builder = WebApplication.CreateBuilder(args);

// Load environment variables from .env file
var envPath = Path.Combine(Directory.GetCurrentDirectory(), ".env");
if (File.Exists(envPath))
{
    var lines = File.ReadAllLines(envPath);
    foreach (var line in lines)
    {
        if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#"))
            continue;

        var parts = line.Split('=', 2);
        if (parts.Length == 2)
        {
            Environment.SetEnvironmentVariable(parts[0].Trim(), parts[1].Trim());
        }
    }
}

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddHttpClient();
builder.Services.AddScoped<TelnyxCallService>();
builder.Services.AddLogging();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();

// Models/CallModels.cs
using Newtonsoft.Json;

namespace TelnyxHoldMusic.Models
{
    public class InitiateCallRequest
    {
        [JsonProperty("to")]
        public string To { get; set; }
    }

    public class CallResponse
    {
        [JsonProperty("call_control_id")]
        public string CallControlId { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }
    }

    public class WebhookEvent
    {
        [JsonProperty("data")]
        public WebhookData Data { get; set; }
    }

    public class WebhookData
    {
        [JsonProperty("event_type")]
        public string EventType { get; set; }

        [JsonProperty("call_control_id")]
        public string CallControlId { get; set; }

        [JsonProperty("state")]
        public string State { get; set; }
    }
}

// Services/TelnyxCallService.cs
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using TelnyxHoldMusic.Models;

namespace TelnyxHoldMusic.Services
{
    public class TelnyxCallService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _phoneNumber;
        private readonly string _connectionId;
        private readonly string _holdMusicUrl;
        private const string BaseUrl = "https://api.telnyx.com/v2";

        public TelnyxCallService(IHttpClientFactory httpClientFactory, IConfiguration config)
        {
            _httpClient = httpClientFactory.CreateClient();
            _apiKey = config["Telnyx:ApiKey"] ?? Environment.GetEnvironmentVariable("TELNYX_API_KEY");
            _phoneNumber = config["Telnyx:PhoneNumber"] ?? Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER");
            _connectionId = config["Telnyx:ConnectionId"] ?? Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID");
            _holdMusicUrl = config["Telnyx:HoldMusicUrl"] ?? Environment.GetEnvironmentVariable("HOLD_MUSIC_URL");

            // Configure default authorization header for all requests
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", _apiKey);
        }

        public async Task<CallResponse> InitiateCallAsync(string toNumber)
        {
            if (string.IsNullOrEmpty(toNumber))
                throw new ArgumentException("Phone number is required", nameof(toNumber));

            if (!toNumber.StartsWith("+"))
                throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)", nameof(toNumber));

            var payload = new
            {
                from_ = _phoneNumber,
                to = toNumber,
                connection_id = _connectionId,
                webhook_url = Environment.GetEnvironmentVariable("WEBHOOK_URL")
            };

            var content = new StringContent(
                JsonConvert.SerializeObject(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync($"{BaseUrl}/calls", content);
            response.EnsureSuccessStatusCode();

            var responseBody = await response.Content.ReadAsStringAsync();
            var callData = JsonConvert.DeserializeObject<dynamic>(responseBody);

            return new CallResponse
            {
                CallControlId = callData.data.call_control_id,
                Status = callData.data.state
            };
        }

        public async Task PlayHoldMusicAsync(string callControlId)
        {
            if (string.IsNullOrEmpty(callControlId))
                throw new ArgumentException("Call control ID is required", nameof(callControlId));

            var payload = new
            {
                audio_url = _holdMusicUrl,
                loop = true
            };

            var content = new StringContent(
                JsonConvert.SerializeObject(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                $"{BaseUrl}/calls/{callControlId}/actions/playback_start",
                content
            );

            response.EnsureSuccessStatusCode();
        }

        public async Task HangupCallAsync(string callControlId)
        {
            if (string.IsNullOrEmpty(callControlId))
                throw new ArgumentException("Call control ID is required", nameof(callControlId));

            var payload = new { };

            var content = new StringContent(
                JsonConvert.SerializeObject(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                $"{BaseUrl}/calls/{callControlId}/actions/hangup",
                content
            );

            response.EnsureSuccessStatusCode();
        }
    }
}

// Controllers/CallsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxHoldMusic.Models;
using TelnyxHoldMusic.Services;

namespace TelnyxHoldMusic.Controllers
{
    [ApiController]
    [Route("api/calls")]
    public class CallsController : ControllerBase
    {
        private readonly TelnyxCallService _callService;
        private readonly ILogger<CallsController> _logger;

        public CallsController(TelnyxCallService callService, ILogger<CallsController> logger)
        {
            _callService = callService;
            _logger = logger;
        }

        [HttpPost("initiate")]
        public async Task<IActionResult> InitiateCall([FromBody] InitiateCallRequest request)
        {
            if (request == null || string.IsNullOrEmpty(request.To))
                return BadRequest(new { error = "Missing required field: 'to'" });

            try
            {
                var callResponse = await _callService.InitiateCallAsync(request.To);
                return Ok(new
                {
                    call_control_id = callResponse.CallControlId,
                    status = callResponse.Status
                });
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
                _logger.LogWarning("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode((int?)ex.StatusCode ?? 500, new { error = "Failed to initiate call" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpPost("{callControlId}/hangup")]
        public async Task<IActionResult> HangupCall(string callControlId)
        {
            if (string.IsNullOrEmpty(callControlId))
                return BadRequest(new { error = "Call control ID is required" });

            try
            {
                await _callService.HangupCallAsync(callControlId);
                return Ok(new { status = "hangup_initiated" });
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode((int?)ex.StatusCode ?? 500, new { error = "Failed to hangup call" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}

// Controllers/WebhooksController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxHoldMusic.Models;
using TelnyxHoldMusic.Services;

namespace TelnyxHoldMusic.Controllers
{
    [ApiController]
    [Route("webhooks")]
    public class WebhooksController : ControllerBase
    {
        private readonly TelnyxCallService _callService;
        private readonly ILogger<WebhooksController> _logger;

        public WebhooksController(TelnyxCallService callService, ILogger<WebhooksController> logger)
        {
            _callService = callService;
            _logger = logger;
        }

        [HttpPost("call")]
        public async Task<IActionResult> HandleCallEvent([FromBody] WebhookEvent webhookEvent)
        {
            if (webhookEvent?.Data == null)
                return BadRequest(new { error = "Invalid webhook payload" });

            var eventType = webhookEvent.Data.EventType;
            var callControlId = webhookEvent.Data.CallControlId;

            _logger.LogInformation($"Received event: {eventType} for call: {callControlId}");

            try
            {
                // When call is answered, start playing hold music
                if (eventType == "call.answered")
                {
                    _logger.LogInformation($"Call answered: {callControlId}. Starting hold music.");
                    await _callService.PlayHoldMusicAsync(callControlId);
                }

                // Log call hangup for cleanup
                if (eventType == "call.hangup")
                {
                    _logger.LogInformation($"Call ended: {callControlId}");
                }

                return Ok(new { status = "processed" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(503, new { error = "Failed to process call event" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}
