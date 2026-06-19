# SIM Activation with Java and Spring

## What Does This Example Do?

Build a production-ready Spring Boot endpoint that activates SIM cards using the Telnyx Java SDK. This tutorial demonstrates the new client-based initialization pattern, proper error handling for IoT APIs, and secure credential management via environment variables. You'll learn how to retrieve SIM card details and activate them programmatically.

## Who Is This For?

- **Java developers** building iot features with Spring.
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
- Maven 3.6+ or Gradle 6.0+.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- At least one SIM card in your Telnyx account (in `ready` or `standby` status).
- Spring Boot 2.7+ or 3.0+.

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-java
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/activate-sim-card-java
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create a service class to handle SIM card activation logic:

```java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.SimCard;
import com.telnyx.model.SimCardActivateResponse;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class SimCardService {

    private final TelnyxClient telnyxClient;

    public SimCardService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    /**
     * Retrieve SIM card details by ID.
     * Returns a map with essential SIM card information.
     */
    public Map<String, Object> getSimCard(String simCardId) throws TelnyxException {
        SimCard simCard = telnyxClient.simCards().retrieve(simCardId);

        return Map.of(
            "id", simCard.getId(),
            "iccid", simCard.getIccid() != null ? simCard.getIccid() : "N/A",
            "status", simCard.getStatus() != null ? simCard.getStatus() : "unknown",
            "simCardGroupId", simCard.getSimCardGroupId() != null ? simCard.getSimCardGroupId() : "N/A"
        );
    }

    /**
     * Activate a SIM card by ID.
     * The SIM must be in 'ready' or 'standby' status.
     * Returns activation response with updated status.
     */
    public Map<String, Object> activateSimCard(String simCardId) throws TelnyxException {
        // Validate SIM ID format
        if (simCardId == null || simCardId.trim().isEmpty()) {
            throw new IllegalArgumentException("SIM card ID cannot be empty");
        }

        // Call the Telnyx API to activate the SIM
        SimCardActivateResponse response = telnyxClient.simCards().activate(simCardId);

        // Extract and return serializable data
        SimCard activatedSim = response.getData();
        return Map.of(
            "id", activatedSim.getId(),
            "iccid", activatedSim.getIccid() != null ? activatedSim.getIccid() : "N/A",
            "status", activatedSim.getStatus() != null ? activatedSim.getStatus() : "unknown",
            "simCardGroupId", activatedSim.getSimCardGroupId() != null ? activatedSim.getSimCardGroupId() : "N/A",
            "message", "SIM card activated successfully"
        );
    }
}
```

## Complete Code

See [`Application.java`](./Application.java) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error": "Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. Restart the Spring Boot application after updating the `.env` file. The SDK reads the environment variable at startup via `TelnyxOkHttpClient.fromEnv()`. |
| SIM Card Not Found | You receive a 400 or 404 error stating the SIM card ID does not exist. | Confirm the SIM card ID is correct by checking your [Telnyx Portal](https://portal.telnyx.com) under IoT → SIM Cards. SIM card IDs typically start with `sim_`. Ensure you are using the full ID, not a partial or truncated version. |
| SIM Card Cannot Be Activated | The API returns an error indicating the SIM is in an invalid state (e.g., already active or suspended). | SIM cards can only be activated from `ready` or `standby` status. Check the current status using the GET endpoint. If the SIM is already `active`, no further activation is needed. If it is `suspended`, you may need to unsuspend it first via the Telnyx Portal or API. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this IoT example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Java version do I need?**

Java 17 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [IoT SIM Get Started](https://developers.telnyx.com/docs/iot-sim/get-started)
- [SIM Card API Reference](https://developers.telnyx.com/api-reference/sim-cards/get-all-sim-cards)
- [Java SDK](https://developers.telnyx.com/development/sdk/java)
- [Telnyx IoT SIM Cards](https://telnyx.com/products/iot-sim-card)
- [IoT Data Plans Pricing](https://telnyx.com/pricing/iot-data-plans)

## Related Examples

- [Monitor SIM Card Data Usage](/tutorials/iot/java/data-usage-monitoring).
- [Configure APN Settings for SIM Cards](/tutorials/iot/java/apn-configuration).
- [Set Up SIM Status Change Webhooks](/tutorials/iot/java/sim-status-webhook).
