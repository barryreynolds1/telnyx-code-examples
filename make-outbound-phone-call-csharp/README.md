# Outbound Call with C# and ASP.NET

## What Does This Example Do?

Build a production-ready ASP.NET endpoint that initiates outbound calls using the Telnyx Voice API. This tutorial demonstrates secure credential management via environment variables, proper HTTP client configuration with Bearer token authentication, and comprehensive error handling for telecom APIs. You'll learn the command-event model where calls are initiated via REST and controlled through webhook events.

## Who Is This For?

- **C# developers** building voice features with ASP.NET.
- **Backend engineers** integrating telephony or messaging into existing applications.
- **DevOps teams** looking for containerized, production-ready telecom examples.
- **Startups and enterprises** replacing legacy telecom providers with a modern API-first platform.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that gives developers a single API for [voice](https://telnyx.com/products/voice-ai-agents), [messaging](https://telnyx.com/products/sms-api), [SIP](https://telnyx.com/products/sip-trunks), [AI](https://telnyx.com/ai-assistants), and [IoT](https://telnyx.com/products/iot-sim-card) — no Frankenstack required.

- **Integrated platform** — [Voice](https://telnyx.com/products/voice-ai-agents), [SMS](https://telnyx.com/products/sms-api), [SIP trunking](https://telnyx.com/products/sip-trunks), [AI assistants](https://telnyx.com/ai-assistants), and [IoT SIM management](https://telnyx.com/products/iot-sim-card) under one roof. No stitching together multiple vendors.
- **Global private network** — Calls and messages traverse the Telnyx-owned IP network for lower latency and higher reliability than the public internet.
- **Developer-first** — SDKs for Python, Node.js, Go, Ruby, Java, and PHP. Comprehensive webhook event model. Sandbox environment for testing.
- **Competitive pricing** — Pay-as-you-go with no minimums, contracts, or per-seat fees.

## Prerequisites

- .NET 6.0 or higher installed.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application ID (connection_id) configured in the Telnyx Portal.
- A publicly accessible webhook URL (or ngrok for local testing).
- Visual Studio, Visual Studio Code, or the .NET CLI.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-csharp
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-csharp
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle call initiation. Add a new file `CallService.cs`:

```csharp
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
        
        // Configure Bearer token authentication
        _httpClient.DefaultRequestHeaders.Authorization =
            new System.Net.Http.Headers.AuthenticationHeaderValue(
                "Bearer", _config.ApiKey);
    }

    public async Task<CallResponse> InitiateCallAsync(string toNumber)
    {
        // Validate E.164 format to prevent API errors
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

        // Handle Telnyx-specific error responses
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

// Internal classes for JSON deserialization
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
```

Create a controller to expose the call initiation endpoint. Add a new file `CallController.cs`:

```csharp
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
        // Validate request body
        if (request == null || string.IsNullOrWhiteSpace(request.To))
        {
            return BadRequest(new { error = "Missing required field: 'to'" });
        }

        try
        {
            var callResponse = await _callService.InitiateCallAsync(request.To);
            
            // Return JSON-serializable response
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
```

Register the `CallService` in `Program.cs`:

```csharp
builder.Services.AddScoped<CallService>();
```

## Complete Code

See [`Program.cs`](./Program.cs) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the ASP.NET development server after updating the `.env` file. |
| Invalid Phone Number Format | You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination. | Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers. |
| Environment Variable Not Set | The application throws `InvalidOperationException: TELNYX_API_KEY not set` on startup. | Confirm your `.env` file exists in the project root directory (same level as `Program.cs`) and contains all three required variables: `TELNYX_API_KEY`, `TELNYX_PHONE_NUMBER`, and `TELNYX_CONNECTION_ID`. Ensure the file is named exactly `.env` (not `.env.txt`). The `Env.Load()` call in `Program.cs` must execute before `TelnyxConfig.FromEnvironment()` is called. |
| Connection ID Not Found | The API returns a 422 error mentioning "connection_id" or "Call Control Application". | Verify that `TELNYX_CONNECTION_ID` in your `.env` file matches a valid Call Control Application ID from the [Telnyx Portal](https://portal.telnyx.com). The connection ID links your phone number to a Call Control application. Create a new Call Control Application if needed and update the environment variable. |
| SSL Certificate Validation Error | When testing locally, you get an SSL certificate validation error. | Use the `-k` flag with curl to bypass certificate validation for local testing: `curl -k https://localhost:5001/...`. In production, use a valid SSL certificate. Alternatively, test against `http://localhost:5000` if you configure ASP.NET to use HTTP. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this Voice example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What C# version do I need?**

.NET 8.0 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Voice API Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [AI Assistant Start](https://developers.telnyx.com/docs/voice/programmable-voice/ai-assistant-start)
- [Call Control API Reference](https://developers.telnyx.com/api-reference/call-commands/dial)
- [Telnyx Voice API](https://telnyx.com/products/voice-api)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [Handle Inbound Call Webhooks with C#](/tutorials/voice/csharp/inbound-call-webhook).
- [Record Calls with C#](/tutorials/voice/csharp/call-recording).
- [Transfer Calls with C#](/tutorials/voice/csharp/call-transfer).
