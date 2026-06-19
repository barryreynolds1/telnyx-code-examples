# SIP Trunking Setup with C# and ASP.NET

## What Does This Example Do?

Build a production-ready ASP.NET application that manages SIP trunk connections using the Telnyx REST API. This tutorial demonstrates secure credential management, proper HTTP client configuration with Bearer token authentication, comprehensive error handling, and JSON serialization patterns for telecom APIs. You'll create endpoints to list, create, and retrieve SIP connections—the foundation for integrating your PBX or SBC with Telnyx.

## Who Is This For?

- **C# developers** building sip features with ASP.NET.
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

- .NET 6.0 or higher installed on your system.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Visual Studio, Visual Studio Code, or the .NET CLI.
- A basic understanding of ASP.NET Core and REST APIs.
- curl or Postman for testing HTTP endpoints.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-csharp
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-csharp
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle SIP connection operations. Add `Services/SipConnectionService.cs`:

```csharp
using System.Text;
using System.Text.Json;
using TelnyxSipTrunking.Models;

namespace TelnyxSipTrunking.Services
{
    public class SipConnectionService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<SipConnectionService> _logger;

        public SipConnectionService(HttpClient httpClient, ILogger<SipConnectionService> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        /// <summary>
        /// List all SIP connections for the account.
        /// </summary>
        public async Task<List<SipConnectionResponse>> ListConnectionsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/sip_connections");
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<SipConnectionListResponse>(content, options);

                return result?.Data ?? new List<SipConnectionResponse>();
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error listing SIP connections: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Create a new SIP connection with credential-based authentication.
        /// </summary>
        public async Task<SipConnectionResponse> CreateConnectionAsync(SipConnectionRequest request)
        {
            try
            {
                // Validate required fields
                if (string.IsNullOrWhiteSpace(request.Name))
                    throw new ArgumentException("Connection name is required");
                if (string.IsNullOrWhiteSpace(request.Username))
                    throw new ArgumentException("Username is required");
                if (string.IsNullOrWhiteSpace(request.Password))
                    throw new ArgumentException("Password is required");
                if (request.SipUris == null || request.SipUris.Count == 0)
                    throw new ArgumentException("At least one SIP URI is required");

                var payload = new
                {
                    data = new
                    {
                        name = request.Name,
                        username = request.Username,
                        password = request.Password,
                        sip_uris = request.SipUris,
                        connection_type = request.ConnectionType
                    }
                };

                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/sip_connections", content);
                response.EnsureSuccessStatusCode();

                var responseContent = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<dynamic>(responseContent, options);

                // Extract the connection data from the response
                var connectionData = JsonSerializer.Deserialize<SipConnectionResponse>(
                    JsonSerializer.Serialize(result), options);

                return connectionData;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error creating SIP connection: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Retrieve a specific SIP connection by ID.
        /// </summary>
        public async Task<SipConnectionResponse> GetConnectionAsync(string connectionId)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(connectionId))
                    throw new ArgumentException("Connection ID is required");

                var response = await _httpClient.GetAsync($"/sip_connections/{connectionId}");
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<dynamic>(content, options);

                var connectionData = JsonSerializer.Deserialize<SipConnectionResponse>(
                    JsonSerializer.Serialize(result), options);

                return connectionData;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error retrieving SIP connection: {ex.Message}");
                throw;
            }
        }
    }
}
```

Create the API controller to expose SIP connection endpoints. Add `Controllers/SipConnectionsController.cs`:

```csharp
using Microsoft.AspNetCore.Mvc;
using TelnyxSipTrunking.Models;
using TelnyxSipTrunking.Services;

namespace TelnyxSipTrunking.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SipConnectionsController : ControllerBase
    {
        private readonly SipConnectionService _sipService;
        private readonly ILogger<SipConnectionsController> _logger;

        public SipConnectionsController(SipConnectionService sipService, ILogger<SipConnectionsController> logger)
        {
            _sipService = sipService;
            _logger = logger;
        }

        /// <summary>
        /// GET /api/sipconnections
        /// List all SIP connections.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> ListConnections()
        {
            try
            {
                var connections = await _sipService.ListConnectionsAsync();
                return Ok(new { data = connections });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
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
        /// POST /api/sipconnections
        /// Create a new SIP connection.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> CreateConnection([FromBody] SipConnectionRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { error = "Invalid request body" });
            }

            try
            {
                var connection = await _sipService.CreateConnectionAsync(request);
                return CreatedAtAction(nameof(GetConnection), new { id = connection.Id }, connection);
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
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error: {ex.Message}");
                return StatusCode(500, new { error = "Failed to create SIP connection" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        /// <summary>
        /// GET /api/sipconnections/{id}
        /// Retrieve a specific SIP connection by ID.
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetConnection(string id)
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return BadRequest(new { error = "Connection ID is required" });
            }

            try
            {
                var connection = await _sipService.GetConnectionAsync(id);
                return Ok(connection);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
            {
                return NotFound(new { error = "SIP connection not found" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                _logger.LogError("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error: {ex.Message}");
                return StatusCode(500, new { error = "Failed to retrieve SIP connection" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}
```

## Complete Code

See [`Program.cs`](./Program.cs) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401 status. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes around the key value. If the key was regenerated recently, update your `.env` file and restart the ASP.NET application with `dotnet run`. |
| Environment Variable Not Set | The application throws `InvalidOperationException: TELNYX_API_KEY environment variable is not set` on startup. | Confirm your `.env` file exists in the project root directory and contains the `TELNYX_API_KEY` variable. Ensure the file is named exactly `.env` (not `.env.txt` or `env`). The environment variables must be loaded before the application starts. Verify the file is not in `.gitignore` if you're using version control. |
| Rate Limit Exceeded (429) | The endpoint returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429 status. | Telnyx API enforces rate limits on requests. Implement exponential backoff retry logic in your service layer. Space out API calls by at least 100ms between requests. For bulk operations, consider batching requests or using pagination with the `page_size` parameter. Check the [Telnyx API documentation](https://developers.telnyx.com) for current rate limit thresholds. |
| Network Error (503) | The endpoint returns `{"error": "Network error connecting to Telnyx"}` with HTTP 503 status. | Verify your internet connection and that `api.telnyx.com` is reachable. Check if Telnyx API is experiencing downtime by visiting the [Telnyx Status Page](https://status.telnyx.com). Ensure your firewall or proxy is not blocking HTTPS requests to `api.telnyx.com`. Implement retry logic with exponential backoff for transient network failures. |
| Invalid SIP URI Format | The endpoint returns a 400 error about invalid SIP URI format when creating a connection. | SIP URIs must follow the format `sip.example.com:5060` or `sip.example.com:5061` for TLS. Ensure the hostname is resolvable and the port is correct (5060 for UDP/TCP, 5061 for TLS). Do not include the `sip://` scheme in the URI—provide only the host and port. Verify your PBX or SBC is listening on the specified port. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SIP example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What C# version do I need?**

.NET 8.0 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [SIP Trunking Get Started](https://developers.telnyx.com/docs/voice/sip-trunking/get-started)
- [SIP Configuration Guides](https://developers.telnyx.com/docs/voice/sip-trunking/configuration-guides)
- [Telnyx SIP Trunks](https://telnyx.com/products/sip-trunks)
- [SIP Trunking Pricing](https://telnyx.com/pricing/elastic-sip)

## Related Examples

- [Configure SIP Registration with Telnyx](/tutorials/sip/csharp/sip-registration).
- [Set Up Outbound SIP Calls](/tutorials/sip/csharp/outbound-sip-call).
- [Implement Failover Routing for SIP Trunks](/tutorials/sip/csharp/failover-routing).
