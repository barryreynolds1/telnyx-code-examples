// Program.cs
using DotNetEnv;

var builder = WebApplicationBuilder.CreateBuilder(args);

// Load environment variables from .env file
Env.Load();

// Add services to the container
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

// ============================================================================

// Services/VoicemailService.cs
using System.Net.Http.Headers;
using System.Text.Json;

namespace TelnyxVoicemail.Services
{
    public class VoicemailService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _phoneNumber;
        private readonly string _connectionId;

        public VoicemailService()
        {
            _apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY")
                ?? throw new InvalidOperationException("TELNYX_API_KEY not set");
            _phoneNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER")
                ?? throw new InvalidOperationException("TELNYX_PHONE_NUMBER not set");
            _connectionId = Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID")
                ?? throw new InvalidOperationException("TELNYX_CONNECTION_ID not set");

            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", _apiKey);
            _httpClient.BaseAddress = new Uri("https://api.telnyx.com/v2");
        }

        public async Task<Dictionary<string, object>> InitiateCallAsync(string toNumber)
        {
            if (!toNumber.StartsWith("+"))
            {
                throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
            }

            var payload = new
            {
                from_ = _phoneNumber,
                to = toNumber,
                connection_id = _connectionId,
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                System.Text.Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync("/calls", content);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to initiate call: {response.StatusCode} - {errorContent}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(responseBody);
            var root = doc.RootElement;

            return new Dictionary<string, object>
            {
                { "call_control_id", root.GetProperty("data").GetProperty("call_control_id").GetString() },
                { "status", root.GetProperty("data").GetProperty("status").GetString() },
            };
        }

        public async Task<Dictionary<string, object>> StartRecordingAsync(string callControlId)
        {
            var payload = new
            {
                format = "wav",
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                System.Text.Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(
                $"/calls/{callControlId}/actions/start_recording",
                content);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to start recording: {response.StatusCode} - {errorContent}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(responseBody);
            var root = doc.RootElement;

            return new Dictionary<string, object>
            {
                { "call_control_id", root.GetProperty("data").GetProperty("call_control_id").GetString() },
                { "recording_started", true },
            };
        }

        public async Task<Dictionary<string, object>> StopRecordingAsync(string callControlId)
        {
            var response = await _httpClient.PostAsync(
                $"/calls/{callControlId}/actions/stop_recording",
                new StringContent("", System.Text.Encoding.UTF8, "application/json"));

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to stop recording: {response.StatusCode} - {errorContent}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(responseBody);
            var root = doc.RootElement;

            return new Dictionary<string, object>
            {
                { "call_control_id", root.GetProperty("data").GetProperty("call_control_id").GetString() },
                { "recording_stopped", true },
            };
        }

        public async Task<Dictionary<string, object>> HangupCallAsync(string callControlId)
        {
            var response = await _httpClient.PostAsync(
                $"/calls/{callControlId}/actions/hangup",
                new StringContent("", System.Text.Encoding.UTF8, "application/json"));

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Failed to hangup call: {response.StatusCode} - {errorContent}");
            }

            return new Dictionary<string, object>
            {
                { "call_control_id", callControlId },
                { "hangup_sent", true },
            };
        }
    }
}

// ============================================================================

// Controllers/VoicemailController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxVoicemail.Services;
using System.Text.Json;

namespace TelnyxVoicemail.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class VoicemailController : ControllerBase
    {
        private readonly VoicemailService _voicemailService;
        private readonly ILogger<VoicemailController> _logger;

        public VoicemailController(ILogger<VoicemailController> logger)
        {
            _logger = logger;
            _voicemailService = new VoicemailService();
        }

        [HttpPost("initiate")]
        public async Task<IActionResult> InitiateVoicemail([FromBody] InitiateVoicemailRequest request)
        {
            if (string.IsNullOrEmpty(request.ToNumber))
            {
                return BadRequest(new { error = "Missing required field: 'toNumber'" });
            }

            try
            {
                var result = await _voicemailService.InitiateCallAsync(request.ToNumber);
                return Ok(result);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "API error initiating call");
                return StatusCode(503, new { error = "Failed to initiate call" });
            }
        }

        [HttpPost("webhook")]
        public async Task<IActionResult> HandleWebhook([FromBody] JsonElement payload)
        {
            try
            {
                var eventType = payload.GetProperty("data").GetProperty("event_type").GetString();
                var callControlId = payload.GetProperty("data").GetProperty("call_control_id").GetString();

                _logger.LogInformation($"Received event: {eventType} for call: {callControlId}");

                switch (eventType)
                {
                    case "call.initiated":
                        _logger.LogInformation($"Call initiated: {callControlId}");
                        break;

                    case "call.answered":
                        _logger.LogInformation($"Call answered: {callControlId}. Starting recording...");
                        await _voicemailService.StartRecordingAsync(callControlId);
                        break;

                    case "call.hangup":
                        _logger.LogInformation($"Call ended: {callControlId}. Stopping recording...");
                        await _voicemailService.StopRecordingAsync(callControlId);
                        break;

                    case "call.recording.saved":
                        var recordingUrl = payload.GetProperty("data").GetProperty("recording_urls")
                            .GetProperty("wav").GetString();
                        _logger.LogInformation($"Recording saved for call {callControlId}: {recordingUrl}");
                        break;

                    default:
                        _logger.LogWarning($"Unhandled event type: {eventType}");
                        break;
                }

                return Ok(new { status = "received" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing webhook");
                return StatusCode(500, new { error = "Webhook processing failed" });
            }
        }

        [HttpPost("stop-recording/{callControlId}")]
        public async Task<IActionResult> StopRecording(string callControlId)
        {
            if (string.IsNullOrEmpty(callControlId))
            {
                return BadRequest(new { error = "Missing required parameter: callControlId" });
            }

            try
            {
                var result = await _voicemailService.StopRecordingAsync(callControlId);
                return Ok(result);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "API error stopping recording");
                return StatusCode(503, new { error = "Failed to stop recording" });
            }
        }

        [HttpPost("hangup/{callControlId}")]
        public async Task<IActionResult> HangupCall(string callControlId)
        {
            if (string.IsNullOrEmpty(callControlId))
            {
                return BadRequest(new { error = "Missing required parameter: callControlId" });
            }

            try
            {
                var result = await _voicemailService.HangupCallAsync(callControlId);
                return Ok(result);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "API error hanging up call");
                return StatusCode(503, new { error = "Failed to hangup call" });
            }
        }
    }

    public class InitiateVoicemailRequest
    {
        public string ToNumber { get; set; }
    }
}
