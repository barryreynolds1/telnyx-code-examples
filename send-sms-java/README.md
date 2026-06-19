# Send a Single SMS with Java and Spring Boot

## What Does This Example Do?

Build a production-ready Spring Boot REST API that sends SMS messages using the Telnyx Java SDK. This tutorial demonstrates the new client-based initialization pattern, proper exception handling for telecom APIs, and secure credential management via environment variables.

## Who Is This For?

- **Java developers** building sms features with Spring.
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

- Java 17 or higher
- Maven 3.6+ or Gradle 7+
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com)
- A Telnyx phone number enabled for outbound SMS
- cURL or Postman for testing

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/send-sms-java
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create `src/main/java/com/telnyx/sms/SmsApplication.java` with the service layer. The service initializes the Telnyx client using the new pattern and validates phone numbers before sending:

```java
package com.telnyx.sms;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.TelnyxOkHttpClient;
import com.telnyx.sdk.model.MessageRequest;
import com.telnyx.sdk.model.MessageResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

@Service
public class SmsService {
    private final TelnyxClient client;
    private final String fromNumber;

    public SmsService(@Value("${TELNYX_PHONE_NUMBER}") String fromNumber) {
        if (fromNumber == null || fromNumber.isEmpty()) {
            throw new IllegalStateException("TELNYX_PHONE_NUMBER environment variable not set");
        }
        this.fromNumber = fromNumber;
        // Initialize client using new pattern — reads TELNYX_API_KEY from environment
        this.client = TelnyxOkHttpClient.fromEnv();
    }

    public Map<String, Object> sendSms(String toNumber, String message) {
        // Validate E.164 format to prevent API errors
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
        }

        MessageRequest msgRequest = MessageRequest.builder()
                .from(fromNumber)
                .to(toNumber)
                .text(message)
                .build();

        // Use client.messages().create() — NOT static client.messages.create()
        MessageResponse response = client.messages().create(msgRequest);

        // Extract serializable data — do not return raw response object
        Map<String, Object> result = new HashMap<>();
        result.put("message_id", response.getData().getId());
        if (response.getData().getTo() != null && !response.getData().getTo().isEmpty()) {
            result.put("status", response.getData().getTo().get(0).getStatus());
        } else {
            result.put("status", "unknown");
        }
        result.put("from", fromNumber);
        result.put("to", toNumber);
        
        return result;
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

### Issue 1: Authentication Error (401)

**Problem:** The endpoint returns `{"error": "Invalid API key"}` with HTTP 401.

**Solution:** Verify your `TELNYX_API_KEY` environment variable is exported in your shell session. The `TelnyxOkHttpClient.fromEnv()` method reads this automatically. Check that the key matches the one in the [Telnyx Portal](https://portal.telnyx.com) with no trailing spaces. If running in an IDE, ensure environment variables are configured in the run configuration and the application was restarted after changes.

### Issue 2: Invalid Phone Number Format

**Problem:** You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination.

**Solution:** Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces, dashes, or parentheses. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers. The validation logic in `SmsService` checks for the leading `+` before calling the API.

### Issue 3: Environment Variable Not Set

**Problem:** The application fails to start with `IllegalStateException: TELNYX_PHONE_NUMBER environment variable not set`.

**Solution:** Confirm you have exported `TELNYX_PHONE_NUMBER` in your environment. For local development, you can create a `.env` file and use a tool like `dotenv-cli`, or set it directly: `export TELNYX_PHONE_NUMBER="+15551234567"`. If using an IDE, add the environment variable to your Spring Boot run configuration. Ensure the value is not empty or null in your `application.properties`—the service constructor validates this at startup.

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SMS example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Java version do I need?**

Java 17 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Messaging Overview](https://developers.telnyx.com/docs/messaging)
- [Send an SMS — Quickstart](https://developers.telnyx.com/docs/messaging/messages/send-message)
- [Messaging API Reference](https://developers.telnyx.com/api-reference/messages/send-a-message)
- [Java SDK](https://developers.telnyx.com/development/sdk/java)
- [Telnyx SMS API](https://telnyx.com/products/sms-api)
- [Messaging Pricing](https://telnyx.com/pricing/messaging)

## Related Examples

- [Send Bulk SMS Messages](/tutorials/sms/java/send-bulk-sms)
- [Receive SMS Webhooks with Java](/tutorials/sms/java/receive-sms-webhook)
- [Implement Two-Factor Authentication with SMS](/tutorials/sms/java/otp-2fa)
