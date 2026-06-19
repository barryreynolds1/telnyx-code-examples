# SIP Trunking Setup with Java and Spring

## What Does This Example Do?

Build a production-ready Spring Boot application that manages SIP trunk connections using the Telnyx Java SDK. This tutorial demonstrates how to create, retrieve, and list SIP connections for integrating your PBX or SBC with Telnyx's carrier-grade SIP infrastructure. You'll learn proper credential management, error handling for telecom APIs, and REST endpoint design for SIP trunk provisioning.

## Who Is This For?

- **Java developers** building sip features with Spring.
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
- A publicly accessible IP address or domain for your SIP endpoint (required for inbound call routing).
- Basic familiarity with Spring Boot and REST APIs.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-java
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle SIP connection operations:

```java
package com.telnyx.sip.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.sip.SipConnection;
import com.telnyx.model.sip.SipConnectionCreateRequest;
import com.telnyx.model.sip.SipConnectionListResponse;
import com.telnyx.model.sip.SipConnectionResponse;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SipConnectionService {

    private final TelnyxClient telnyxClient;

    public SipConnectionService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    /**
     * Create a new SIP connection with credential-based authentication.
     * Validates required fields before API call.
     */
    public Map<String, Object> createSipConnection(
            String name,
            String username,
            String password,
            String sipAddress) throws TelnyxException {

        // Validate required fields
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Connection name is required");
        }
        if (username == null || username.isBlank()) {
            throw new IllegalArgumentException("Username is required");
        }
        if (password == null || password.isBlank()) {
            throw new IllegalArgumentException("Password is required");
        }
        if (sipAddress == null || sipAddress.isBlank()) {
            throw new IllegalArgumentException("SIP address is required");
        }

        // Build request parameters
        SipConnectionCreateRequest request = new SipConnectionCreateRequest();
        request.setName(name);
        request.setUsername(username);
        request.setPassword(password);
        request.setSipAddress(sipAddress);

        // Create connection via Telnyx API
        SipConnectionResponse response = telnyxClient.sipConnections().create(request);

        // Extract serializable data — SDK objects are NOT JSON-serializable
        return extractSipConnectionData(response.getData());
    }

    /**
     * Retrieve a specific SIP connection by ID.
     */
    public Map<String, Object> getSipConnection(String connectionId) throws TelnyxException {
        if (connectionId == null || connectionId.isBlank()) {
            throw new IllegalArgumentException("Connection ID is required");
        }

        SipConnectionResponse response = telnyxClient.sipConnections().retrieve(connectionId);
        return extractSipConnectionData(response.getData());
    }

    /**
     * List all SIP connections with pagination support.
     */
    public List<Map<String, Object>> listSipConnections(Integer pageSize) throws TelnyxException {
        SipConnectionListResponse response = telnyxClient.sipConnections()
                .list(pageSize != null ? pageSize : 20);

        // Extract serializable data from list — NEVER return response.getData() directly
        return response.getData().stream()
                .map(this::extractSipConnectionData)
                .toList();
    }

    /**
     * Extract JSON-serializable fields from SipConnection object.
     * This prevents serialization errors when returning SDK objects in HTTP responses.
     */
    private Map<String, Object> extractSipConnectionData(SipConnection connection) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", connection.getId());
        data.put("name", connection.getName());
        data.put("username", connection.getUsername());
        data.put("sipAddress", connection.getSipAddress());
        data.put("createdAt", connection.getCreatedAt());
        data.put("updatedAt", connection.getUpdatedAt());
        return data;
    }
}
```

Create a REST controller to expose SIP connection endpoints:

```java
package com.telnyx.sip.controller;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.sip.service.SipConnectionService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/sip-connections")
public class SipConnectionController {

    private final SipConnectionService sipConnectionService;

    public SipConnectionController(SipConnectionService sipConnectionService) {
        this.sipConnectionService = sipConnectionService;
    }

    /**
     * POST /sip-connections
     * Create a new SIP connection with credential-based authentication.
     */
    @PostMapping
    public ResponseEntity<?> createSipConnection(
            @RequestBody Map<String, String> request) {

        try {
            String name = request.get("name");
            String username = request.get("username");
            String password = request.get("password");
            String sipAddress = request.get("sip_address");

            Map<String, Object> result = sipConnectionService.createSipConnection(
                    name, username, password, sipAddress);

            return ResponseEntity.status(HttpStatus.CREATED).body(result);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * GET /sip-connections/{id}
     * Retrieve a specific SIP connection by ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getSipConnection(@PathVariable String id) {
        try {
            Map<String, Object> result = sipConnectionService.getSipConnection(id);
            return ResponseEntity.ok(result);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * GET /sip-connections
     * List all SIP connections with optional pagination.
     */
    @GetMapping
    public ResponseEntity<?> listSipConnections(
            @RequestParam(required = false) Integer pageSize) {

        try {
            List<Map<String, Object>> result = sipConnectionService.listSipConnections(pageSize);
            return ResponseEntity.ok(Map.of("data", result));

        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}
```

Create the main Spring Boot application class:

```java
package com.telnyx.sip;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SipTrunkingApplication {

    public static void main(String[] args) {
        SpringApplication.run(SipTrunkingApplication.class, args);
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` environment variable is set correctly. Run `echo $TELNYX_API_KEY` to confirm the value. Ensure there are no trailing spaces or quotes. If the key was regenerated in the [Telnyx Portal](https://portal.telnyx.com), update your environment and restart the Spring Boot application with `mvn spring-boot:run`. |
| Missing Required Fields | You receive a 400 error stating "Connection name is required" or similar validation error. | Ensure your POST request includes all required fields: `name`, `username`, `password`, and `sip_address`. Verify the JSON payload is properly formatted and uses the correct field names (snake_case in JSON, camelCase in Java). Example: `{"name": "My PBX", "username": "user", "password": "pass", "sip_address": "pbx.example.com:5060"}`. |
| Rate Limit Exceeded (429) | The endpoint returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429. | The Telnyx API enforces rate limits. Implement exponential backoff in your client: wait 1 second, then 2 seconds, then 4 seconds between retries. For production, cache SIP connection data and avoid repeated list/retrieve calls. Check the [Telnyx API documentation](https://developers.telnyx.com) for current rate limit thresholds. |
| Connection Refused | The application fails to start or returns connection errors to Telnyx API. | Ensure your machine has outbound internet access to `api.telnyx.com`. Verify firewall rules allow HTTPS (port 443). Check that the Telnyx Java SDK is properly included in `pom.xml` with version `2.0.0` or later. Run `mvn dependency:tree` to confirm all transitive dependencies are resolved. |
| SIP Address Format Invalid | The API returns an error about invalid SIP address format. | SIP addresses must follow the format `host:port` or `host` (defaults to port 5060). Examples: `pbx.example.com:5060`, `192.168.1.100:5061`, or `sip.example.com`. Ensure the hostname is resolvable and the port is accessible from Telnyx's infrastructure. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this SIP example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Java version do I need?**

Java 17 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [SIP Trunking Get Started](https://developers.telnyx.com/docs/voice/sip-trunking/get-started)
- [SIP Configuration Guides](https://developers.telnyx.com/docs/voice/sip-trunking/configuration-guides)
- [Java SDK](https://developers.telnyx.com/development/sdk/java)
- [Telnyx SIP Trunks](https://telnyx.com/products/sip-trunks)
- [SIP Trunking Pricing](https://telnyx.com/pricing/elastic-sip)

## Related Examples

- [Configure SIP Registration with Java](/tutorials/sip/java/sip-registration).
- [Set Up Outbound SIP Calls with Java](/tutorials/sip/java/outbound-sip-call).
- [Implement Failover Routing for SIP Trunks](/tutorials/sip/java/failover-routing).
