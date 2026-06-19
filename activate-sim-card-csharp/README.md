# SIM Activation with C# and ASP.NET

## What Does This Example Do?

Build a production-ready ASP.NET endpoint that activates SIM cards using the Telnyx IoT API. This tutorial demonstrates secure credential management via environment variables, proper error handling for telecom APIs, and JSON serialization patterns for ASP.NET Core. You'll create an endpoint that accepts a SIM card ID and activates it with optional configuration parameters.

## Who Is This For?

- **C# developers** building iot features with ASP.NET.
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
- At least one SIM card in your Telnyx account (in `ready` or `standby` status).
- Visual Studio, Visual Studio Code, or the .NET CLI.
- curl or Postman for testing HTTP endpoints.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-csharp
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-csharp
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a new controller file `Controllers/SimCardController.cs` to handle SIM activation requests:

```csharp
using Microsoft.AspNetCore.Mvc;
using System.Net.Http.Headers;
using System.Text.Json;

namespace TelnyxSimActivation.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SimCardController : ControllerBase
    {
        private readonly ILogger<SimCardController> _logger;
        private readonly HttpClient _httpClient;

        public SimCardController(ILogger<SimCardController> logger)
        {
            _logger = logger;
            _httpClient = new HttpClient();
            
            // Configure HTTP client with Telnyx API base URL and authentication
            _httpClient.BaseAddress = new Uri("https://api.telnyx.com/v2/");
            var apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY");
            if (string.IsNullOrEmpty(apiKey))
            {
                throw new InvalidOperationException("TELNYX_API_KEY environment variable not set");
            }
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", apiKey);
            _httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        /// <summary>
        /// Activate a SIM card by ID.
        /// </summary>
        [HttpPost("activate")]
        public async Task<IActionResult> ActivateSimCard([FromBody] ActivateSimRequest request)
        {
            // Validate request payload
            if (string.IsNullOrWhiteSpace(request?.SimCardId))
            {
                return BadRequest(new { error = "Missing required field: 'sim_card_id'" });
            }

            try
            {
                // Build request payload for Telnyx API
                var payload = new
                {
                    activation_settings = new
                    {
                        apn = request.Apn ?? "internet.telnyx"
                    }
                };

                var jsonContent = new StringContent(
                    JsonSerializer.Serialize(payload),
                    System.Text.Encoding.UTF8,
                    "application/json");

                // Send activation request to Telnyx API
                var response = await _httpClient.PostAsync(
                    $"sim_cards/{request.SimCardId}/actions/activate",
                    jsonContent);

                // Handle API response
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return HandleApiError(response.StatusCode, responseContent);
                }

                // Parse and extract serializable response data
                using (JsonDocument doc = JsonDocument.Parse(responseContent))
                {
                    var root = doc.RootElement;
                    if (root.TryGetProperty("data", out var dataElement))
                    {
                        var simData = dataElement;
                        return Ok(new
                        {
                            id = simData.GetProperty("id").GetString(),
                            iccid = simData.GetProperty("iccid").GetString(),
                            status = simData.GetProperty("status").GetString(),
                            sim_card_group_id = simData.TryGetProperty("sim_card_group_id", out var groupId) 
                                ? groupId.GetString() 
                                : null,
                            message = "SIM card activation initiated"
                        });
                    }
                }

                return Ok(new { message = "SIM card activation initiated" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// Get SIM card details by ID.
        /// </summary>
        [HttpGet("{simCardId}")]
        public async Task<IActionResult> GetSimCard(string simCardId)
        {
            if (string.IsNullOrWhiteSpace(simCardId))
            {
                return BadRequest(new { error = "SIM card ID is required" });
            }

            try
            {
                var response = await _httpClient.GetAsync($"sim_cards/{simCardId}");
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return HandleApiError(response.StatusCode, responseContent);
                }

                // Parse and extract serializable response data
                using (JsonDocument doc = JsonDocument.Parse(responseContent))
                {
                    var root = doc.RootElement;
                    if (root.TryGetProperty("data", out var dataElement))
                    {
                        var simData = dataElement;
                        return Ok(new
                        {
                            id = simData.GetProperty("id").GetString(),
                            iccid = simData.GetProperty("iccid").GetString(),
                            status = simData.GetProperty("status").GetString(),
                            sim_card_group_id = simData.TryGetProperty("sim_card_group_id", out var groupId) 
                                ? groupId.GetString() 
                                : null
                        });
                    }
                }

                return Ok(new { message = "SIM card retrieved" });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"Network error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// Handle Telnyx API errors and map to appropriate HTTP status codes.
        /// </summary>
        private IActionResult HandleApiError(System.Net.HttpStatusCode statusCode, string responseContent)
        {
            return statusCode switch
            {
                System.Net.HttpStatusCode.Unauthorized => 
                    Unauthorized(new { error = "Invalid API key" }),
                System.Net.HttpStatusCode.TooManyRequests => 
                    StatusCode(429, new { error = "Rate limit exceeded. Please slow down." }),
                System.Net.HttpStatusCode.NotFound => 
                    NotFound(new { error = "SIM card not found" }),
                System.Net.HttpStatusCode.BadRequest => 
                    BadRequest(new { error = "Invalid request parameters", details = responseContent }),
                _ => 
                    StatusCode((int)statusCode, new { error = "Telnyx API error", details = responseContent })
            };
        }
    }

    /// <summary>
    /// Request model for SIM card activation.
    /// </summary>
    public class ActivateSimRequest
    {
        public string SimCardId { get; set; }
        public string Apn { get; set; }
    }
}
```

## Complete Code

See [`Program.cs`](./Program.cs) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Confirm the `.env` file is in the project root and `DotNetEnv.Env.Load()` is called in `Program.cs` before any API requests. Restart the application after updating the key. |
| SIM Card Not Found (404) | The endpoint returns `{"error": "SIM card not found"}` with HTTP 404. | Verify the SIM card ID is correct by checking your [Telnyx Portal](https://portal.telnyx.com) under IoT → SIM Cards. Ensure the SIM card exists and is in a state that allows activation (typically `ready` or `standby` status). Copy the full ID from the portal and paste it into your request. |
| Network Error (503) | The endpoint returns `{"error": "Network error connecting to Telnyx"}` with HTTP 503. | Check your internet connection and firewall settings. Verify that `https://api.telnyx.com` is accessible from your network. If behind a corporate proxy, configure the `HttpClient` to use the proxy. Ensure the Telnyx API service is operational by checking the [Telnyx Status Page](https://status.telnyx.com). |
| Invalid Request Parameters (400) | The endpoint returns `{"error": "Invalid request parameters"}` with HTTP 400. | Verify the JSON payload is correctly formatted and includes the required `sim_card_id` field. Ensure the APN (if provided) is a valid string. Check the Telnyx API documentation for the correct activation settings format. Review the `details` field in the response for specific validation errors from the API. |
| Environment Variable Not Set | The application throws `InvalidOperationException: TELNYX_API_KEY environment variable not set` on startup. | Confirm your `.env` file exists in the project root directory and contains `TELNYX_API_KEY=YOUR_API_KEY_HERE`. Ensure the file is named exactly `.env` (not `.env.txt` or `env`). Verify `DotNetEnv.Env.Load()` is called at the beginning of `Program.cs` before the API key is accessed. Restart the application after creating or updating the `.env` file. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this IoT example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What C# version do I need?**

.NET 8.0 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [IoT SIM Get Started](https://developers.telnyx.com/docs/iot-sim/get-started)
- [SIM Card API Reference](https://developers.telnyx.com/api-reference/sim-cards/get-all-sim-cards)
- [Telnyx IoT SIM Cards](https://telnyx.com/products/iot-sim-card)
- [IoT Data Plans Pricing](https://telnyx.com/pricing/iot-data-plans)

## Related Examples

- [Monitor SIM Card Data Usage](/tutorials/iot/csharp/data-usage-monitoring).
- [Configure Custom APN Settings](/tutorials/iot/csharp/apn-configuration).
- [Handle SIM Status Change Webhooks](/tutorials/iot/csharp/sim-status-webhook).
