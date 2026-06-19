// Program.cs
using DotNetEnv;
using TelnyxOutboundCall;

Env.Load();

var builder = WebApplicationBuilder.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSingleton<TelnyxConfig>(TelnyxConfig.FromEnvironment());
builder.Services.AddHttpClient();
builder.Services.AddScoped<CallService>();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();

// TelnyxConfig.cs
namespace TelnyxOutboundCall;

public class TelnyxConfig
{
    public string ApiKey { get; set; }
    public string PhoneNumber { get; set; }
    public string ConnectionId { get; set; }

    public static TelnyxConfig FromEnvironment()
    {
        return new TelnyxConfig
        {
            ApiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY") 
                ?? throw new InvalidOperationException("TELNYX_API_KEY not set"),
            PhoneNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER") 
                ?? throw new InvalidOperationException("TELNYX_PHONE_NUMBER not set"),
            ConnectionId = Environment.GetEnvironmentVariable("TELNYX_CONNECTION_ID") 
                ?? throw new InvalidOperationException("TELNYX_CONNECTION_ID not set"),
        };
    }
}

// CallService.cs
using Newtonsoft.Json;

namespace TelnyxOutboundCall;

public class CallService
{
    private readonly HttpClient _httpClient;
    private readonly TelnyxConfig _config;
    private const string ApiBaseUrl = "https://api.telnyx.com/v2";

    public CallService(HttpClient httpClient, TelnyxConfig config)
    {
        _httpClient = httpClient;
        _config = config;
        
        _httpClient.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue(
                "Bearer", _config.ApiKey);
    }

    public async Task<CallResponse> InitiateCallAsync(string toNumber)
    {
        if (!toNumber.StartsWith("+"))
        {
            throw new ArgumentException(
                "Phone number must be in E.164 format (e.g., +15551234567)");
        }

        var payload = new
        {
            from_ = _config.PhoneNumber,
            to = toNumber,
            connection_id = _config.ConnectionId,
        };

        var content = new StringContent(
            JsonConvert.SerializeObject(payload),
            System.Text.Encoding.UTF8,
            "application/json");

        var response = await _httpClient.PostAsync(
            $"{ApiBaseUrl}/calls",
            content);

        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync();
            throw new HttpRequestException(
                $"Telnyx API error ({response.StatusCode}): {errorContent}");
        }

        var responseBody = await response.Content.ReadAsStringAsync();
        var result = JsonConvert.DeserializeObject<TelnyxApiResponse>(responseBody);

        if (result?.Data == null)
        {
            throw new InvalidOperationException("Invalid response from Telnyx API");
        }

        return new CallResponse
        {
            CallControlId = result.Data.CallControlId,
            State = result.Data.State,
            From = result.Data.From,
            To = result.Data.To,
        };
    }
}

public class CallResponse
{
    public string CallControlId { get; set; }
    public string State { get; set; }
    public string From { get; set; }
    public string To { get; set; }
}

internal class TelnyxApiResponse
{
    [JsonProperty("data")]
    public CallData Data { get; set; }
}

internal class CallData
{
    [JsonProperty("call_control_id")]
    public string CallControlId { get; set; }

    [JsonProperty("state")]
    public string State { get; set; }

    [JsonProperty("from")]
    public string From { get; set; }

    [JsonProperty("to")]
    public string To { get; set; }
}

// CallController.cs
using Microsoft.AspNetCore.Mvc;

namespace TelnyxOutboundCall.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CallController : ControllerBase
{
    private readonly CallService _callService;
    private readonly ILogger<CallController> _logger;

    public CallController(CallService callService, ILogger<CallController> logger)
    {
        _callService = callService;
        _logger = logger;
    }

    [HttpPost("initiate")]
    public async Task<IActionResult> InitiateCall([FromBody] InitiateCallRequest request)
    {
        if (request == null || string.IsNullOrWhiteSpace(request.To))
        {
            return BadRequest(new { error = "Missing required field: 'to'" });
        }

        try
        {
            var callResponse = await _callService.InitiateCallAsync(request.To);
            
            return Ok(new
            {
                call_control_id = callResponse.CallControlId,
                state = callResponse.State,
                from = callResponse.From,
                to = callResponse.To,
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
            _logger.LogError($"API error: {ex.Message}");
            return StatusCode(503, new { error = "Network error connecting to Telnyx" });
        }
        catch (Exception ex)
        {
            _logger.LogError($"Unexpected error: {ex.Message}");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }
}

public class InitiateCallRequest
{
    public string To { get; set; }
}
