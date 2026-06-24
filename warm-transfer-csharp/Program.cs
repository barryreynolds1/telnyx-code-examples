// Program.cs
using TelnyxWarmTransfer.Configuration;
using TelnyxWarmTransfer.Services;
using DotNetEnv;

var builder = WebApplication.CreateBuilder(args);

// Load environment variables from .env file
Env.Load();

// Configure Telnyx settings
var telnyxSettings = new TelnyxSettings
{
    ApiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY"),
    PhoneNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER"),
    ConnectionId = Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID"),
    Agent1Number = Environment.GetEnvironmentVariable("TELNYX_AGENT_1_NUMBER"),
    Agent2Number = Environment.GetEnvironmentVariable("TELNYX_AGENT_2_NUMBER"),
};

builder.Services.AddSingleton(telnyxSettings);

// Configure HTTP client for Telnyx API
builder.Services.AddHttpClient("TelnyxClient", client =>
{
    client.BaseAddress = new Uri("https://api.telnyx.com/v2/");
    client.DefaultRequestHeaders.Add("Authorization", $"Bearer {telnyxSettings.ApiKey}");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});

builder.Services.AddScoped<ICallControlService, CallControlService>();
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

// Configuration/TelnyxSettings.cs
namespace TelnyxWarmTransfer.Configuration
{
    public class TelnyxSettings
    {
        public string ApiKey { get; set; }
        public string PhoneNumber { get; set; }
        public string ConnectionId { get; set; }
        public string Agent1Number { get; set; }
        public string Agent2Number { get; set; }
    }
}

// Services/ICallControlService.cs
namespace TelnyxWarmTransfer.Services
{
    public interface ICallControlService
    {
        Task<(string CallControlId, string Error)> InitiateCallAsync(string toNumber);
        Task<(bool Success, string Error)> TransferCallAsync(string callControlId, string transferTo);
        Task<(bool Success, string Error)> HangupCallAsync(string callControlId);
    }
}

// Services/CallControlService.cs
using TelnyxWarmTransfer.Configuration;
using Newtonsoft.Json;

namespace TelnyxWarmTransfer.Services
{
    public class CallControlService : ICallControlService
    {
        private readonly HttpClient _httpClient;
        private readonly TelnyxSettings _settings;
        private readonly ILogger<CallControlService> _logger;

        public CallControlService(
            IHttpClientFactory httpClientFactory,
            TelnyxSettings settings,
            ILogger<CallControlService> logger)
        {
            _httpClient = httpClientFactory.CreateClient("TelnyxClient");
            _settings = settings;
            _logger = logger;
        }

        public async Task<(string CallControlId, string Error)> InitiateCallAsync(string toNumber)
        {
            try
            {
                if (!toNumber.StartsWith("+"))
                {
                    return (null, "Phone number must be in E.164 format (e.g., +15551234567)");
                }

                var payload = new
                {
                    from_ = _settings.PhoneNumber,
                    to = toNumber,
                    connection_id = _settings.ConnectionId,
                };

                var content = new StringContent(
                    JsonConvert.SerializeObject(payload),
                    System.Text.Encoding.UTF8,
                    "application/json");

                var response = await _httpClient.PostAsync("calls", content);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError($"Telnyx API error: {response.StatusCode} - {errorContent}");
                    return (null, $"Failed to initiate call: {response.StatusCode}");
                }

                var responseContent = await response.Content.ReadAsStringAsync();
                dynamic responseData = JsonConvert.DeserializeObject(responseContent);
                string callControlId = responseData.data.call_control_id;

                _logger.LogInformation($"Call initiated with ID: {callControlId}");
                return (callControlId, null);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                return (null, "Network error connecting to Telnyx");
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return (null, ex.Message);
            }
        }

        public async Task<(bool Success, string Error)> TransferCallAsync(string callControlId, string transferTo)
        {
            try
            {
                if (string.IsNullOrEmpty(callControlId))
                {
                    return (false, "Call control ID is required");
                }

                if (!transferTo.StartsWith("+"))
                {
                    return (false, "Transfer number must be in E.164 format");
                }

                var payload = new
                {
                    to = transferTo,
                };

                var content = new StringContent(
                    JsonConvert.SerializeObject(payload),
                    System.Text.Encoding.UTF8,
                    "application/json");

                var response = await _httpClient.PostAsync(
                    $"calls/{callControlId}/actions/transfer",
                    content);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError($"Transfer failed: {response.StatusCode} - {errorContent}");
                    return (false, $"Transfer failed: {response.StatusCode}");
                }

                _logger.LogInformation($"Call {callControlId} transferred to {transferTo}");
                return (true, null);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error during transfer: {ex.Message}");
                return (false, "Network error connecting to Telnyx");
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error during transfer: {ex.Message}");
                return (false, ex.Message);
            }
        }

        public async Task<(bool Success, string Error)> HangupCallAsync(string callControlId)
        {
            try
            {
                if (string.IsNullOrEmpty(callControlId))
                {
                    return (false, "Call control ID is required");
                }

                var payload = new { };

                var content = new StringContent(
                    JsonConvert.SerializeObject(payload),
                    System.Text.Encoding.UTF8,
                    "application/json");

                var response = await _httpClient.PostAsync(
                    $"calls/{callControlId}/actions/hangup",
                    content);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError($"Hangup failed: {response.StatusCode} - {errorContent}");
                    return (false, $"Hangup failed: {response.StatusCode}");
                }

                _logger.LogInformation($"Call {callControlId} hung up");
                return (true, null);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error during hangup: {ex.Message}");
                return (false, "Network error connecting to Telnyx");
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error during hangup: {ex.Message}");
                return (false, ex.Message);
            }
        }
    }
}

// Controllers/CallsController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxWarmTransfer.Services;
using Newtonsoft.Json;

namespace TelnyxWarmTransfer.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CallsController : ControllerBase
    {
        private readonly ICallControlService _callControlService;
        private readonly ILogger<CallsController> _logger;

        public CallsController(
            ICallControlService callControlService,
            ILogger<CallsController> logger)
        {
            _callControlService = callControlService;
            _logger = logger;
        }

        [HttpPost("initiate")]
        public async Task<IActionResult> InitiateCall([FromBody] InitiateCallRequest request)
        {
            if (string.IsNullOrEmpty(request?.ToNumber))
            {
                return BadRequest(new { error = "Missing required field: 'toNumber'" });
            }

            var (callControlId, error) = await _callControlService.InitiateCallAsync(request.ToNumber);

            if (!string.IsNullOrEmpty(error))
            {
                return BadRequest(new { error });
            }

            return Ok(new { call_control_id = callControlId });
        }

        [HttpPost("transfer")]
        public async Task<IActionResult> TransferCall([FromBody] TransferCallRequest request)
        {
            if (string.IsNullOrEmpty(request?.CallControlId) || string.IsNullOrEmpty(request?.TransferTo))
            {
                return BadRequest(new { error = "Missing required fields: 'callControlId' and 'transferTo'" });
            }

            var (success, error) = await _callControlService.TransferCallAsync(request.CallControlId, request.TransferTo);

            if (!success)
            {
                return BadRequest(new { error });
            }

            return Ok(new { message = "Call transferred successfully" });
        }

        [HttpPost("hangup")]
        public async Task<IActionResult> HangupCall([FromBody] HangupCallRequest request)
        {
            if (string.IsNullOrEmpty(request?.CallControlId))
            {
                return BadRequest(new { error = "Missing required field: 'callControlId'" });
            }

            var (success, error) = await _callControlService.HangupCallAsync(request.CallControlId);

            if (!success)
            {
                return BadRequest(new { error });
            }

            return Ok(new { message = "Call hung up successfully" });
        }

        [HttpPost("webhook")]
        public IActionResult HandleWebhook([FromBody] dynamic webhookData)
        {
            try
            {
                string eventType = webhookData.data.event_type;
                string callControlId = webhookData.data.call_control_id;

                _logger.LogInformation($"Webhook received: {eventType} for call {callControlId}");

                switch (eventType)
                {
                    case "call.initiated":
                        _logger.LogInformation($"Call initiated: {callControlId}");
                        break;
                    case "call.answered":
                        _logger.LogInformation($"Call answered: {callControlId}");
                        break;
                    case "call.hangup":
                        _logger.LogInformation($"Call ended: {callControlId}");
                        break;
                    default:
                        _logger.LogInformation($"Unhandled event: {eventType}");
                        break;
                }

                return Ok(new { message = "Webhook processed" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Webhook processing error: {ex.Message}");
                return Ok(new { message = "Webhook received" });
            }
        }
    }

    public class InitiateCallRequest
    {
        [JsonProperty("toNumber")]
        public string ToNumber { get; set; }
    }

    public class TransferCallRequest
    {
        [JsonProperty("callControlId")]
        public string CallControlId { get; set; }

        [JsonProperty("transferTo")]
        public string TransferTo { get; set; }
    }

    public class HangupCallRequest
    {
        [JsonProperty("callControlId")]
        public string CallControlId { get; set; }
    }
}
