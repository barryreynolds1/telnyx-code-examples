# Receive SMS Webhook with C# and ASP.NET

## What Does This Example Do?

Build a production-ready ASP.NET Core endpoint that receives inbound SMS messages via Telnyx webhooks. This tutorial demonstrates webhook validation, secure credential management via environment variables, and proper error handling for telecom events. You'll configure a Messaging Profile to route inbound SMS to your endpoint and process incoming messages in real time.

## Who Is This For?

- **C# developers** building sms features with ASP.NET.
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
- A Telnyx phone number enabled for inbound SMS.
- A publicly accessible URL (ngrok, Cloudflare Tunnel, or deployed server) to receive webhooks.
- Visual Studio, Visual Studio Code, or the .NET CLI.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-csharp
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-csharp
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a `Models` folder and add a webhook event model to deserialize incoming SMS events:

```csharp
// Models/WebhookEvent.cs
namespace TelnyxSmsWebhook.Models
{
    public class WebhookEvent
    {
        public string? EventType { get; set; }
        public MessageData? Data { get; set; }
    }

    public class MessageData
    {
        public string? Id { get; set; }
        public string? Direction { get; set; }
        public string? From { get; set; }
        public string? To { get; set; }
        public string? Text { get; set; }
        public string? Type { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}
```

Create a controller to handle incoming webhook requests:

```csharp
// Controllers/WebhookController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSmsWebhook.Models;
using System.Security.Cryptography;
using System.Text;

namespace TelnyxSmsWebhook.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class WebhookController : ControllerBase
    {
        private readonly ILogger<WebhookController> _logger;

        public WebhookController(ILogger<WebhookController> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Receives inbound SMS webhooks from Telnyx.
        /// Validates webhook signature and processes message.received events.
        /// </summary>
        [HttpPost("sms")]
        public IActionResult ReceiveSmsWebhook([FromBody] WebhookEvent? webhookEvent)
        {
            // Validate request body
            if (webhookEvent == null)
            {
                _logger.LogWarning("Received webhook with null body");
                return BadRequest(new { error = "Request body required" });
            }

            // Validate webhook signature from request headers
            var signatureHeader = Request.Headers["Telnyx-Signature-Token"].ToString();
            if (string.IsNullOrEmpty(signatureHeader))
            {
                _logger.LogWarning("Received webhook without signature token");
                return Unauthorized(new { error = "Missing signature token" });
            }

            // Verify signature to ensure request came from Telnyx
            if (!VerifyWebhookSignature(signatureHeader))
            {
                _logger.LogWarning("Webhook signature verification failed");
                return Unauthorized(new { error = "Invalid signature" });
            }

            // Process only message.received events (inbound SMS)
            if (webhookEvent.EventType != "message.received")
            {
                _logger.LogInformation($"Ignoring event type: {webhookEvent.EventType}");
                return Ok(new { status = "ignored" });
            }

            // Extract message data
            var messageData = webhookEvent.Data;
            if (messageData == null)
            {
                _logger.LogWarning("Received message.received event with null data");
                return BadRequest(new { error = "Message data missing" });
            }

            // Log the inbound message
            _logger.LogInformation(
                $"Inbound SMS received - ID: {messageData.Id}, From: {messageData.From}, To: {messageData.To}, Text: {messageData.Text}"
            );

            // Return success response to Telnyx (prevents retry)
            return Ok(new
            {
                status = "received",
                message_id = messageData.Id,
                from = messageData.From,
                to = messageData.To,
                text = messageData.Text
            });
        }

        /// <summary>
        /// Verifies the webhook signature using HMAC-SHA256.
        /// Telnyx signs each webhook with your webhook signing secret.
        /// </summary>
        private bool VerifyWebhookSignature(string signature)
        {
            var secret = Environment.GetEnvironmentVariable("WEBHOOK_SIGNING_SECRET");
            if (string.IsNullOrEmpty(secret))
            {
                _logger.LogError("WEBHOOK_SIGNING_SECRET environment variable not set");
                return false;
            }

            try
            {
                // Read the raw request body for signature verification
                Request.Body.Position = 0;
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEndAsync().Result;
                    Request.Body.Position = 0;

                    // Compute HMAC-SHA256 of the request body
                    using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret)))
                    {
                        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(body));
                        var computedSignature = Convert.ToBase64String(hash);

                        // Compare computed signature with provided signature
                        return computedSignature == signature;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error verifying webhook signature: {ex.Message}");
                return false;
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
| Webhook signature verification fails | The endpoint returns `{"error": "Invalid signature"}` with HTTP 401. | Verify that your `WEBHOOK_SIGNING_SECRET` in the `.env` file matches the signing secret configured in your Telnyx Messaging Profile. The secret must be identical on both sides. Ensure the `.env` file is loaded before the application starts by checking that `Env.Load()` is called in `Program.cs`. |
| Webhook URL not receiving requests | You configure the webhook URL in the Telnyx Portal but no requests arrive at your endpoint. | Ensure your public URL (from ngrok or your deployed server) is correct and accessible. Test the URL in a browser to confirm it's reachable. Verify that the webhook URL in the Telnyx Portal is set to `https://your-public-url/api/webhook/sms` (note the `/api/webhook/sms` path). Check your firewall and network settings to ensure inbound HTTPS traffic is allowed. |
| Environment variable not set | The application logs show `WEBHOOK_SIGNING_SECRET environment variable not set` or similar errors. | Confirm your `.env` file exists in the project root directory (same level as `Program.cs`). Ensure the file is named exactly `.env` (not `.env.txt` or `env`). Verify that `Env.Load()` is called at the start of `Program.cs` before any environment variable access. Restart the application after creating or modifying the `.env` file. |
| Request body is empty or null | The endpoint receives a webhook but `webhookEvent` is null, returning a 400 error. | Ensure the `Content-Type` header in the webhook request is `application/json`. Verify that your model classes (`WebhookEvent` and `MessageData`) match the JSON structure sent by Telnyx. Check the Telnyx webhook documentation to confirm the exact payload format. Enable request logging in ASP.NET Core to inspect the raw request body. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SMS example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What C# version do I need?**

.NET 8.0 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Messaging Overview](https://developers.telnyx.com/docs/messaging)
- [Send an SMS — Quickstart](https://developers.telnyx.com/docs/messaging/messages/send-message)
- [Messaging API Reference](https://developers.telnyx.com/api-reference/messages/send-a-message)
- [Telnyx SMS API](https://telnyx.com/products/sms-api)
- [Messaging Pricing](https://telnyx.com/pricing/messaging)

## Related Examples

- [Send a Single SMS with C# and ASP.NET](/tutorials/sms/csharp/send-single-sms).
- [Send Bulk SMS Messages with C# and ASP.NET](/tutorials/sms/csharp/send-bulk-sms).
- [Implement Two-Factor Authentication with SMS and C#](/tutorials/sms/csharp/otp-2fa).
