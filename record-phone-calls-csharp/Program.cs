// Program.cs
using DotNetEnv;
using TelnyxCallRecorder;

Env.Load();

var builder = WebApplicationBuilder.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton<TelnyxConfig>();
builder.Services.AddScoped<TelnyxCallService>();
builder.Services.AddHttpClient();

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

// TelnyxConfig.cs
namespace TelnyxCallRecorder;

public class TelnyxConfig
{
    public string ApiKey { get; set; } = Environment.GetEnvironmentVariable("TELNYX_API_KEY") ?? "";
    public string PhoneNumber { get; set; } = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER") ?? "";
    public string ConnectionId { get; set; } = Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID") ?? "";
    public string WebhookUrl { get; set; } = Environment.GetEnvironmentVariable("WEBHOOK_URL") ?? "";

    public void Validate()
    {
        if (string.IsNullOrEmpty(ApiKey))
            throw new InvalidOperationException("TELNYX_API_KEY environment variable not set");
        if (string.IsNullOrEmpty(PhoneNumber))
            throw new InvalidOperationException("TELNYX_PHONE_NUMBER environment variable not set");
        if (string.IsNullOrEmpty(ConnectionId))
            throw new InvalidOperationException("TELNYX_CONNECTION_ID environment variable not set");
    }
}

// TelnyxCallService.cs
using Newtonsoft.Json;
using System.Text;

namespace TelnyxCallRecorder;

public class TelnyxCallService
{
    private readonly HttpClient _httpClient;
    private readonly TelnyxConfig _config;
    private readonly ILogger<TelnyxCallService> _logger;

    public TelnyxCallService(HttpClient httpClient, TelnyxConfig config, ILogger<TelnyxCallService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _logger = logger;
        
        _httpClient.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue(
                "Bearer", _config.ApiKey);
        _httpClient.BaseAddress = new Uri("https://api.telnyx.com/v2");
    }

    public async Task<CallInitiateResponse> InitiateCallWithRecordingAsync(string toNumber)
    {
        if (!toNumber.StartsWith("+"))
            throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");

        var payload = new
        {
            from_ = _config.PhoneNumber,
            to = toNumber,
            connection_id = _config.ConnectionId,
            record = true,
            record_channels = "both",
            record_format = "wav"
        };

        var content = new StringContent(
            JsonConvert.SerializeObject(payload),
            Encoding.UTF8,
            "application/json");

        try
        {
            var response = await _httpClient.PostAsync("/calls", content);
            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError($"Telnyx API error: {response.StatusCode} - {responseBody}");
                throw new TelnyxApiException(response.StatusCode, responseBody);
            }

            var result = JsonConvert.DeserializeObject<TelnyxApiResponse<CallData>>(responseBody);
            if (result?.Data == null)
                throw new InvalidOperationException("Invalid response from Telnyx API");

            return new CallInitiateResponse
            {
                CallControlId = result.Data.CallControlId,
                From = result.Data.From,
                To = result.Data.To,
                State = result.Data.State
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError($"Network error: {ex.Message}");
            throw new TelnyxApiException(System.Net.HttpStatusCode.ServiceUnavailable, "Network error connecting to Telnyx");
        }
    }

    public async Task<bool> StopRecordingAsync(string callControlId)
    {
        var payload = new { };
        var content = new StringContent(
            JsonConvert.SerializeObject(payload),
            Encoding.UTF8,
            "application/json");

        try
        {
            var response = await _httpClient.PostAsync($"/calls/{callControlId}/actions/stop_recording", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var responseBody = await response.Content.ReadAsStringAsync();
                _logger.LogError($"Stop recording error: {response.StatusCode} - {responseBody}");
                throw new TelnyxApiException(response.StatusCode, responseBody);
            }

            return true;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError($"Network error: {ex.Message}");
            throw new TelnyxApiException(System.Net.HttpStatusCode.ServiceUnavailable, "Network error connecting to Telnyx");
        }
    }
}

public class TelnyxApiException : Exception
{
    public System.Net.HttpStatusCode StatusCode { get; }

    public TelnyxApiException(System.Net.HttpStatusCode statusCode, string message)
        : base(message)
    {
        StatusCode = statusCode;
    }
}

public class TelnyxApiResponse<T>
{
    [JsonProperty("data")]
    public T Data { get; set; }
}

public class CallData
{
    [JsonProperty("call_control_id")]
    public string CallControlId { get; set; }

    [JsonProperty("from")]
    public string From { get; set; }

    [JsonProperty("to")]
    public string To { get; set; }

    [JsonProperty("state")]
    public string State { get; set; }
}

public class CallInitiateResponse
{
    public string CallControlId { get; set; }
    public string From { get; set; }
    public string To { get; set; }
    public string State { get; set; }
}

// CallController.cs
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;

namespace TelnyxCallRecorder.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CallController : ControllerBase
{
    private readonly TelnyxCallService _callService;
    private readonly ILogger<CallController> _logger;

    public CallController(TelnyxCallService callService, ILogger<CallController> logger)
    {
        _callService = callService;
        _logger = logger;
    }

    [HttpPost("initiate")]
    public async Task<IActionResult> InitiateCall([FromBody] InitiateCallRequest request)
    {
        if (request == null || string.IsNullOrEmpty(request.ToNumber))
            return BadRequest(new { error = "Missing required field: 'toNumber'" });

        try
        {
            var result = await _callService.InitiateCallWithRecordingAsync(request.ToNumber);
            return Ok(new
            {
                call_control_id = result.CallControlId,
                from = result.From,
                to = result.To,
                state = result.State,
                recording_enabled = true
            });
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
        catch (TelnyxApiException ex)
        {
            _logger.LogError($"Telnyx API error: {ex.Message}");
            
            return ex.StatusCode switch
            {
                System.Net.HttpStatusCode.Unauthorized => Unauthorized(new { error = "Invalid API key" }),
                System.Net.HttpStatusCode.TooManyRequests => StatusCode(429, new { error = "Rate limit exceeded. Please slow down." }),
                System.Net.HttpStatusCode.ServiceUnavailable => StatusCode(503, new { error = "Network error connecting to Telnyx" }),
                _ => StatusCode((int)ex.StatusCode, new { error = ex.Message })
            };
        }
    }

    [HttpPost("webhooks/events")]
    public async Task<IActionResult> HandleCallEvent([FromBody] dynamic eventData)
    {
        try
        {
            string eventType = eventData["data"]["event_type"];
            string callControlId = eventData["data"]["call_control_id"];

            _logger.LogInformation($"Received event: {eventType} for call: {callControlId}");

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
                    try
                    {
                        await _callService.StopRecordingAsync(callControlId);
                        _logger.LogInformation($"Recording stopped for call: {callControlId}");
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning($"Failed to stop recording: {ex.Message}");
                    }
                    break;

                case "call.recording.saved":
                    _logger.LogInformation($"Recording saved for call: {callControlId}");
                    string recordingUrl = eventData["data"]["recording_urls"]?[0];
                    if (!string.IsNullOrEmpty(recordingUrl))
                    {
                        _logger.LogInformation($"Recording available at: {recordingUrl}");
                    }
                    break;

                default:
                    _logger.LogInformation($"Unhandled event type: {eventType}");
                    break;
            }

            return Ok(new { success = true });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Webhook processing error: {ex.Message}");
            return StatusCode(500, new { error = "Webhook processing failed" });
        }
    }
}

public class InitiateCallRequest
{
    [JsonProperty("toNumber")]
    public string ToNumber { get; set; }
}
