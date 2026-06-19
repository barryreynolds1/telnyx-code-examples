# Receive SMS Webhook with Java and Spring

## What Does This Example Do?

Build a production-ready Spring Boot endpoint that receives inbound SMS messages via Telnyx webhooks. This tutorial demonstrates webhook validation, proper error handling for telecom APIs, and secure credential management via environment variables. You'll configure a Messaging Profile to route inbound SMS to your application and process incoming messages in real time.

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

- Java 11 or higher.
- Maven 3.6+ or Gradle 7.0+.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- A Telnyx phone number enabled for inbound SMS.
- A publicly accessible URL (ngrok, Heroku, or similar) to receive webhooks during development.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/receive-sms-webhook-java
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a Spring Boot application class at `src/main/java/com/telnyx/SmsWebhookApplication.java`:

```java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SmsWebhookApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmsWebhookApplication.class, args);
    }
}
```

Create a configuration class at `src/main/java/com/telnyx/config/TelnyxConfig.java` to initialize the Telnyx client:

```java
package com.telnyx.config;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.TelnyxOkHttpClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {
    
    @Value("${telnyx.api.key}")
    private String apiKey;
    
    @Bean
    public TelnyxClient telnyxClient() {
        // Initialize client from environment variable
        return TelnyxOkHttpClient.fromEnv();
    }
}
```

Create a model class at `src/main/java/com/telnyx/model/SmsWebhookPayload.java` to represent incoming webhook data:

```java
package com.telnyx.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class SmsWebhookPayload {
    
    @JsonProperty("data")
    private WebhookData data;
    
    @JsonProperty("meta")
    private Map<String, Object> meta;
    
    public static class WebhookData {
        @JsonProperty("id")
        private String id;
        
        @JsonProperty("type")
        private String type;
        
        @JsonProperty("attributes")
        private MessageAttributes attributes;
        
        public String getId() {
            return id;
        }
        
        public void setId(String id) {
            this.id = id;
        }
        
        public String getType() {
            return type;
        }
        
        public void setType(String type) {
            this.type = type;
        }
        
        public MessageAttributes getAttributes() {
            return attributes;
        }
        
        public void setAttributes(MessageAttributes attributes) {
            this.attributes = attributes;
        }
    }
    
    public static class MessageAttributes {
        @JsonProperty("from")
        private String from;
        
        @JsonProperty("to")
        private List<String> to;
        
        @JsonProperty("text")
        private String text;
        
        @JsonProperty("direction")
        private String direction;
        
        @JsonProperty("received_at")
        private String receivedAt;
        
        public String getFrom() {
            return from;
        }
        
        public void setFrom(String from) {
            this.from = from;
        }
        
        public List<String> getTo() {
            return to;
        }
        
        public void setTo(List<String> to) {
            this.to = to;
        }
        
        public String getText() {
            return text;
        }
        
        public void setText(String text) {
            this.text = text;
        }
        
        public String getDirection() {
            return direction;
        }
        
        public void setDirection(String direction) {
            this.direction = direction;
        }
        
        public String getReceivedAt() {
            return receivedAt;
        }
        
        public void setReceivedAt(String receivedAt) {
            this.receivedAt = receivedAt;
        }
    }
    
    public WebhookData getData() {
        return data;
    }
    
    public void setData(WebhookData data) {
        this.data = data;
    }
    
    public Map<String, Object> getMeta() {
        return meta;
    }
    
    public void setMeta(Map<String, Object> meta) {
        this.meta = meta;
    }
}
```

Create a REST controller at `src/main/java/com/telnyx/controller/SmsWebhookController.java` to handle incoming webhooks:

```java
package com.telnyx.controller;

import com.telnyx.model.SmsWebhookPayload;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/webhooks")
public class SmsWebhookController {
    
    private static final Logger logger = LoggerFactory.getLogger(SmsWebhookController.class);
    
    @PostMapping("/sms")
    public ResponseEntity<Map<String, Object>> receiveSms(@RequestBody SmsWebhookPayload payload) {
        try {
            // Validate webhook payload structure
            if (payload == null || payload.getData() == null) {
                logger.warn("Received invalid webhook payload");
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Invalid webhook payload"));
            }
            
            SmsWebhookPayload.WebhookData data = payload.getData();
            SmsWebhookPayload.MessageAttributes attributes = data.getAttributes();
            
            // Log inbound message details
            logger.info("Received SMS webhook - ID: {}, From: {}, To: {}, Direction: {}",
                data.getId(),
                attributes.getFrom(),
                attributes.getTo(),
                attributes.getDirection());
            
            // Process inbound message (direction == "inbound")
            if ("inbound".equals(attributes.getDirection())) {
                logger.info("Inbound SMS from {} with text: {}",
                    attributes.getFrom(),
                    attributes.getText());
                
                // Add your business logic here:
                // - Store message in database
                // - Trigger automated response
                // - Update user interface
                // - Send to message queue
            }
            
            // Return 200 OK to acknowledge receipt (prevents Telnyx retries)
            return ResponseEntity.ok(Map.of(
                "status", "received",
                "message_id", data.getId()
            ));
            
        } catch (Exception e) {
            logger.error("Error processing SMS webhook", e);
            return ResponseEntity.status(500)
                .body(Map.of("error", "Internal server error"));
        }
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Webhook not triggering | Your endpoint receives no POST requests after sending an SMS to your Telnyx number. | Verify the webhook URL in your Messaging Profile is correct and publicly accessible. Use ngrok to expose your local server: `ngrok http 8080`. Confirm the event type is set to `message.received`. Check that your Telnyx phone number is associated with the correct Messaging Profile. Test with curl to ensure the endpoint responds with HTTP 200. |
| Invalid webhook payload error | The endpoint returns `{"error": "Invalid webhook payload"}` when Telnyx sends a webhook. | Verify the JSON structure matches the expected `SmsWebhookPayload` model. Check that Jackson is properly configured to deserialize the payload. Ensure the `@JsonProperty` annotations match the exact field names in the Telnyx webhook (case-sensitive). Log the raw request body to debug: add `@RequestBody String rawBody` and log it before parsing. |
| Environment variable not loaded | The application fails to start with `TELNYX_API_KEY` not found or null. | Ensure your `.env` file exists in the project root and contains `TELNYX_API_KEY=your_key_here`. For production, set environment variables in your deployment platform (Heroku, AWS, Docker, etc.). Verify Spring is loading properties from `application.properties` which references `${TELNYX_API_KEY}`. Restart the application after updating environment variables. |
| Webhook returns 500 error | Telnyx receives HTTP 500 responses and retries the webhook. | Check Spring Boot logs for exceptions in the `receiveSms` method. Verify all model classes have proper getters and setters. Ensure Jackson dependency is included in `pom.xml`. Test the endpoint with curl using a valid JSON payload to isolate the issue. Add try-catch blocks around business logic to prevent unhandled exceptions. |

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

- [Send a Single SMS with Java and Spring](/tutorials/sms/java/send-single-sms).
- [Send Bulk SMS Messages with Java and Spring](/tutorials/sms/java/send-bulk-sms).
- [Implement Two-Factor Authentication with SMS and Java](/tutorials/sms/java/otp-2fa).
