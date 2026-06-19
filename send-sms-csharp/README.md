# Send a Single SMS with C# and ASP.NET Core

## What Does This Example Do?

Build a production-ready ASP.NET Core Minimal API endpoint that sends SMS messages using the Telnyx C# SDK. This tutorial demonstrates the new client-based initialization pattern, proper error handling for telecom APIs, and secure credential management via environment variables.

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

- .NET 6.0 or higher
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com)
- A Telnyx phone number enabled for outbound SMS
- The `dotnet` CLI

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-csharp
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-csharp
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a request model and initialize the Telnyx client using the new pattern. Add the following to `Program.cs`:

```csharp
using Telnyx;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Initialize client using new pattern — NOT Telnyx.api_key = ...
var client = new TelnyxClient(apiKey: Environment.GetEnvironmentVariable("TELNYX_API_KEY"));
builder.Services.AddSingleton(client);

var app = builder.Build();

// Request model for JSON binding
public class SendSmsRequest
{
    [JsonPropertyName("to")]
    public string To { get; set; }
    
    [JsonPropertyName("message")]
    public string Message { get; set; }
}
```

## Complete Code

See [`Program.cs`](./Program.cs) for the full implementation.

## Troubleshooting

### Issue 1: Authentication Error (401)

**Problem:** The endpoint returns `{"error": "Invalid API key"}` with HTTP 401.

**Solution:** Verify your `TELNYX_API_KEY` environment variable is set correctly. On Windows, use `$env:TELNYX_API_KEY` in PowerShell or set it via System Properties. On macOS/Linux, ensure you exported the variable in the same terminal session running `dotnet run`. Restart the application after setting the variable.

### Issue 2: Invalid Phone Number Format

**Problem:** You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination.

**Solution:** Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers.

### Issue 3: Environment Variable Not Set

**Problem:** The application returns `"TELNYX_PHONE_NUMBER environment variable not set"` or the client initialization fails with a null API key.

**Solution:** Confirm environment variables are set in the terminal before running `dotnet run`. For persistent configuration during development, add them to `launchSettings.json` in the `environmentVariables` section, or use `dotnet user-secrets` to store sensitive configuration securely.

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

- [Send Bulk SMS Messages](/tutorials/sms/csharp/send-bulk-sms)
- [Receive SMS Webhooks with C#](/tutorials/sms/csharp/receive-sms-webhook)
- [Implement Two-Factor Authentication with SMS](/tutorials/sms/csharp/otp-2fa)
