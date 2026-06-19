# Outbound Call with Java and Spring

## What Does This Example Do?

Build a production-ready Spring Boot endpoint that initiates outbound calls using the Telnyx Java SDK. This tutorial demonstrates the client initialization pattern, proper error handling for telecom APIs, secure credential management via environment variables, and the command-event model that powers Telnyx Call Control.

## Who Is This For?

- **Java developers** building voice features with Spring.
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

- Java 11 or higher.
- Maven 3.6+ or Gradle 7.0+.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for outbound calls.
- A Call Control Application ID (connection_id) configured in the Telnyx Portal.
- Spring Boot 2.7+ installed.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/make-outbound-phone-call-java
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a Spring configuration class to initialize the Telnyx client as a singleton bean:

```java
package com.telnyx.config;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {

    @Bean
    public TelnyxClient telnyxClient() {
        // Initialize client from TELNYX_API_KEY environment variable
        return TelnyxOkHttpClient.fromEnv();
    }
}
```

Create a service class to handle call initiation logic:

```java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.CallDialResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class CallService {

    @Autowired
    private TelnyxClient telnyxClient;

    @Value("${TELNYX_PHONE_NUMBER}")
    private String fromNumber;

    @Value("${TELNYX_CONNECTION_ID}")
    private String connectionId;

    /**
     * Initiate an outbound call.
     * 
     * @param toNumber Destination phone number in E.164 format (e.g., +15559876543).
     * @return Map containing call_control_id and other call metadata.
     * @throws IllegalArgumentException if phone number format is invalid.
     * @throws TelnyxException if the API call fails.
     */
    public Map<String, Object> initiateCall(String toNumber) {
        // Validate E.164 format to prevent API errors
        if (toNumber == null || !toNumber.startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15559876543)"
            );
        }

        if (fromNumber == null || fromNumber.isEmpty()) {
            throw new IllegalArgumentException(
                "TELNYX_PHONE_NUMBER environment variable not set"
            );
        }

        if (connectionId == null || connectionId.isEmpty()) {
            throw new IllegalArgumentException(
                "TELNYX_CONNECTION_ID environment variable not set"
            );
        }

        // Initiate the call using the Telnyx SDK
        // connection_id is REQUIRED and links the call to your Call Control Application
        // call_control_id is RETURNED in the response — use it for subsequent actions
        CallDialResponse response = telnyxClient.calls().dial(
            fromNumber,
            toNumber,
            connectionId
        );

        // Extract serializable data — SDK objects are NOT JSON-serializable
        Map<String, Object> result = new HashMap<>();
        result.put("call_control_id", response.getData().getCallControlId());
        result.put("from", fromNumber);
        result.put("to", toNumber);
        result.put("state", response.getData().getState());

        return result;
    }
}
```

Create a REST controller to expose the call initiation endpoint:

```java
package com.telnyx.controller;

import com.telnyx.service.CallService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/calls")
public class CallController {

    @Autowired
    private CallService callService;

    /**
     * HTTP endpoint to initiate an outbound call.
     * 
     * Request body: {"to": "+15559876543"}
     * Response: {"call_control_id": "...", "from": "...", "to": "...", "state": "..."}
     */
    @PostMapping("/initiate")
    public ResponseEntity<Map<String, Object>> initiateCall(@RequestBody Map<String, String> request) {
        // Validate request body
        if (request == null || !request.containsKey("to")) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Missing required field: 'to'");
            return ResponseEntity.badRequest().body(error);
        }

        String toNumber = request.get("to");

        try {
            Map<String, Object> result = callService.initiateCall(toNumber);
            return ResponseEntity.ok(result);

        } catch (IllegalArgumentException e) {
            // Validation error (invalid phone format, missing env vars)
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
}
```

Create a global exception handler to manage Telnyx API errors:

```java
package com.telnyx.exception;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.util.HashMap;
import java.util.Map;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<Map<String, Object>> handleAuthenticationError(AuthenticationException e) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "Invalid API key");
        error.put("details", e.getMessage());
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }

    @ExceptionHandler(RateLimitException.class)
    public ResponseEntity<Map<String, Object>> handleRateLimitError(RateLimitException e) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "Rate limit exceeded. Please slow down.");
        error.put("details", e.getMessage());
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
    }

    @ExceptionHandler(TelnyxException.class)
    public ResponseEntity<Map<String, Object>> handleTelnyxError(TelnyxException e) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "Telnyx API error");
        error.put("details", e.getMessage());
        // Use status code from exception if available, otherwise 500
        int statusCode = e.getStatusCode() != null ? e.getStatusCode() : 500;
        return ResponseEntity.status(statusCode).body(error);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGenericError(Exception e) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", "Internal server error");
        error.put("details", e.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

Create the main Spring Boot application class:

```java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OutboundCallApplication {

    public static void main(String[] args) {
        SpringApplication.run(OutboundCallApplication.class, args);
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in `application.properties` or environment variables matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your configuration and restart the Spring Boot application. |
| Invalid Phone Number Format | You receive a 400 error stating "Phone number must be in E.164 format" or a Telnyx API error about invalid destination. | Ensure all phone numbers use E.164 format: start with `+`, followed by country code and number without spaces or dashes. Example: `+15551234567` (US) or `+447700900123` (UK). Update your test curl command to use properly formatted numbers. |
| Missing Connection ID | The application raises `IllegalArgumentException: TELNYX_CONNECTION_ID environment variable not set` on the first call request. | Confirm your `application.properties` file contains `TELNYX_CONNECTION_ID=your_connection_id` or set the environment variable `export TELNYX_CONNECTION_ID="your_id"`. The connection ID is your Call Control Application ID from the Telnyx Portal—it links your phone number to the Call Control service. Restart the Spring Boot application after updating the configuration. |
| Call Remains in "Parked" State | The call is initiated successfully but never connects to the recipient. | This is normal behavior—the call enters a "parked" state until the recipient answers. Use webhooks to monitor call state changes (call.answered, call.hangup). Configure a webhook URL in your Call Control Application settings in the Telnyx Portal to receive real-time call events. |
| Network Error (503) | The endpoint returns `{"error": "Network error connecting to Telnyx"}` with HTTP 503. | Verify your internet connection and that the Telnyx API is reachable. Check that your firewall or proxy does not block outbound HTTPS connections to `api.telnyx.com`. If the issue persists, check the Telnyx status page for any service disruptions. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this Voice example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Java version do I need?**

Java 17 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [Voice API Overview](https://developers.telnyx.com/docs/voice)
- [Voice API Commands](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-commands-and-resources)
- [AI Assistant Start](https://developers.telnyx.com/docs/voice/programmable-voice/ai-assistant-start)
- [Call Control API Reference](https://developers.telnyx.com/api-reference/call-commands/dial)
- [Java SDK](https://developers.telnyx.com/development/sdk/java)
- [Telnyx Voice API](https://telnyx.com/products/voice-api)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [Receive Inbound Call Webhooks with Java](/tutorials/voice/java/inbound-call-webhook).
- [Record Calls with Java](/tutorials/voice/java/call-recording).
- [Transfer Calls with Java](/tutorials/voice/java/call-transfer).
