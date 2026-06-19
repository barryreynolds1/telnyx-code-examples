# Chat With AI Assistant with Java and Spring

## What Does This Example Do?

Build a production-ready Spring Boot REST API that enables real-time chat interactions with Telnyx AI Assistants. This tutorial demonstrates the Java SDK initialization pattern, proper error handling for AI API calls, secure credential management via environment variables, and JSON serialization of SDK response objects in a Spring context.

## Who Is This For?

- **Java developers** building ai features with Spring.
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
- An existing AI Assistant created in the Telnyx Portal (or you can create one via API).
- Spring Boot 2.7+ or 3.0+.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-java
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

    /**
     * Initialize Telnyx client from environment variables.
     * The SDK reads TELNYX_API_KEY automatically.
     */
    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}
```

Create a service class to handle AI Assistant chat logic:

```java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.AiAssistant;
import com.telnyx.model.ChatMessage;
import com.telnyx.model.ChatResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class AiAssistantService {

    private final TelnyxClient telnyxClient;

    @Value("${telnyx.assistant.id}")
    private String assistantId;

    @Autowired
    public AiAssistantService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    /**
     * Send a message to the AI Assistant and retrieve the response.
     * Returns a plain Map for JSON serialization.
     */
    public Map<String, Object> chatWithAssistant(String userMessage) {
        // Validate input to prevent empty messages
        if (userMessage == null || userMessage.trim().isEmpty()) {
            throw new IllegalArgumentException("Message cannot be empty");
        }

        // Call the Telnyx AI Assistants API
        ChatResponse response = telnyxClient.aiAssistants().chat(
            assistantId,
            userMessage
        );

        // Extract serializable data from SDK response object
        Map<String, Object> result = new HashMap<>();
        result.put("assistant_id", assistantId);
        result.put("user_message", userMessage);
        result.put("assistant_response", response.getData().getMessage());
        result.put("conversation_id", response.getData().getConversationId());
        result.put("tokens_used", response.getData().getTokensUsed());

        return result;
    }

    /**
     * Retrieve assistant metadata to verify it exists and is enabled.
     */
    public Map<String, Object> getAssistantInfo() {
        AiAssistant assistant = telnyxClient.aiAssistants().retrieve(assistantId);

        Map<String, Object> info = new HashMap<>();
        info.put("id", assistant.getId());
        info.put("name", assistant.getName());
        info.put("model", assistant.getModel());
        info.put("enabled_features", assistant.getEnabledFeatures());
        info.put("created_at", assistant.getCreatedAt());

        return info;
    }
}
```

Create a REST controller to expose the chat endpoint:

```java
package com.telnyx.controller;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.service.AiAssistantService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final AiAssistantService aiAssistantService;

    @Autowired
    public ChatController(AiAssistantService aiAssistantService) {
        this.aiAssistantService = aiAssistantService;
    }

    /**
     * POST /api/chat/message
     * Send a message to the AI Assistant and receive a response.
     */
    @PostMapping("/message")
    public ResponseEntity<?> sendMessage(@RequestBody ChatRequest request) {
        // Validate request body
        if (request == null || request.getMessage() == null) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Request body with 'message' field is required");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            Map<String, Object> response = aiAssistantService.chatWithAssistant(request.getMessage());
            return ResponseEntity.ok(response);

        } catch (AuthenticationException e) {
            // 401: Invalid API key
            Map<String, String> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (RateLimitException e) {
            // 429: Rate limit exceeded
            Map<String, String> error = new HashMap<>();
            error.put("error", "Rate limit exceeded. Please slow down.");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);

        } catch (TelnyxException e) {
            // 500: Generic Telnyx API error
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);

        } catch (IllegalArgumentException e) {
            // 400: Validation error
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    /**
     * GET /api/chat/assistant-info
     * Retrieve metadata about the configured AI Assistant.
     */
    @GetMapping("/assistant-info")
    public ResponseEntity<?> getAssistantInfo() {
        try {
            Map<String, Object> info = aiAssistantService.getAssistantInfo();
            return ResponseEntity.ok(info);

        } catch (AuthenticationException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (TelnyxException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Simple request DTO for chat messages.
     */
    public static class ChatRequest {
        private String message;

        public ChatRequest() {}

        public ChatRequest(String message) {
            this.message = message;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }
}
```

Create the main Spring Boot application class:

```java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AiAssistantChatApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiAssistantChatApplication.class, args);
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` environment variable matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the Spring Boot application after updating the environment variable. Check that the variable is exported in your shell session before running `mvn spring-boot:run`. |
| Assistant Not Found | The endpoint returns a 404 or error stating the assistant ID does not exist. | Confirm the `TELNYX_ASSISTANT_ID` environment variable is set to a valid assistant ID from your Telnyx account. Log in to the [Telnyx Portal](https://portal.telnyx.com) and verify the assistant exists and is enabled. Copy the exact ID from the portal and update your environment variable. |
| Rate Limit Exceeded (429) | The endpoint returns `{"error": "Rate limit exceeded. Please slow down."}` with HTTP 429. | The Telnyx API has rate limits per account. Implement exponential backoff in your client code or reduce the frequency of requests. Wait a few seconds before retrying. For production use, consider implementing a message queue to throttle requests. |
| Empty Message Error (400) | The endpoint returns `{"error": "Message cannot be empty"}` when sending a request. | Ensure your JSON request body includes a non-empty `message` field. Example: `{"message": "Hello, assistant!"}`. Verify the message is not just whitespace. |
| Connection Error (503) | The endpoint returns a 503 error or connection timeout. | Verify your internet connection and that the Telnyx API is reachable. Check if your firewall or proxy is blocking outbound HTTPS connections to `api.telnyx.com`. Temporarily disable VPN or proxy to test connectivity. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this AI example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Java version do I need?**

Java 17 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [AI Assistants Guide](https://developers.telnyx.com/docs/inference/ai-assistants/no-code-voice-assistant)
- [Assistants API Reference](https://developers.telnyx.com/api-reference/assistants/create-an-assistant)
- [Java SDK](https://developers.telnyx.com/development/sdk/java)
- [Telnyx AI Assistants](https://telnyx.com/ai-assistants)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [List AI Assistants](/tutorials/ai/java/list-ai-assistants).
- [Create an AI Assistant](/tutorials/ai/java/create-ai-assistant).
- [Update an AI Assistant](/tutorials/ai/java/update-ai-assistant).
