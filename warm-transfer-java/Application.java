// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx</groupId>
    <artifactId>warm-transfer-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>com.telnyx</groupId>
            <artifactId>telnyx-java</artifactId>
            <version>2.0.0</version>
        </dependency>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>

// src/main/resources/application.properties
server.port=8080
telnyx.api.key=${TELNYX_API_KEY}
telnyx.phone.number=${TELNYX_PHONE_NUMBER}
telnyx.connection.id=${TELNYX_CONNECTION_ID}
telnyx.agent.phone=${TELNYX_AGENT_PHONE}

// src/main/java/com/telnyx/config/TelnyxConfig.java
package com.telnyx.config;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.TelnyxOkHttpClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {

    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}

// src/main/java/com/telnyx/service/WarmTransferService.java
package com.telnyx.service;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.exception.ApiException;
import com.telnyx.sdk.model.CallControlCommandResponse;
import com.telnyx.sdk.model.CallDialResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class WarmTransferService {

    @Autowired
    private TelnyxClient telnyxClient;

    @Value("${telnyx.phone.number}")
    private String fromNumber;

    @Value("${telnyx.connection.id}")
    private String connectionId;

    @Value("${telnyx.agent.phone}")
    private String agentPhone;

    public Map<String, String> initiateAgentCall(String originalCallControlId) throws ApiException {
        try {
            CallDialResponse response = telnyxClient.calls().dial(
                    fromNumber,
                    agentPhone,
                    connectionId
            );

            return Map.of(
                    "agent_call_control_id", response.getData().getCallControlId(),
                    "original_call_control_id", originalCallControlId
            );
        } catch (ApiException e) {
            throw e;
        }
    }

    public Map<String, String> completeTransfer(String originalCallControlId, String agentCallControlId) throws ApiException {
        try {
            CallControlCommandResponse response = telnyxClient.calls().actions().transfer(
                    originalCallControlId,
                    agentCallControlId
            );

            return Map.of(
                    "status", "transferred",
                    "original_call_control_id", originalCallControlId,
                    "agent_call_control_id", agentCallControlId
            );
        } catch (ApiException e) {
            throw e;
        }
    }

    public Map<String, String> hangupCall(String callControlId) throws ApiException {
        try {
            telnyxClient.calls().actions().hangup(callControlId);

            return Map.of(
                    "status", "hung_up",
                    "call_control_id", callControlId
            );
        } catch (ApiException e) {
            throw e;
        }
    }
}

// src/main/java/com/telnyx/controller/CallController.java
package com.telnyx.controller;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.telnyx.sdk.exception.ApiException;
import com.telnyx.service.WarmTransferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/calls")
public class CallController {

    @Autowired
    private WarmTransferService warmTransferService;

    @PostMapping("/webhook")
    public ResponseEntity<Map<String, String>> handleWebhook(@RequestBody String payload) {
        try {
            JsonObject event = JsonParser.parseString(payload).getAsJsonObject();
            String eventType = event.get("data").getAsJsonObject().get("event_type").getAsString();
            String callControlId = event.get("data").getAsJsonObject().get("call_control_id").getAsString();

            System.out.println("Received event: " + eventType + " for call: " + callControlId);

            switch (eventType) {
                case "call.initiated":
                    System.out.println("Call initiated: " + callControlId);
                    break;
                case "call.answered":
                    System.out.println("Call answered: " + callControlId);
                    break;
                case "call.hangup":
                    System.out.println("Call hung up: " + callControlId);
                    break;
                default:
                    System.out.println("Unhandled event type: " + eventType);
            }

            return ResponseEntity.ok(Map.of("status", "received"));
        } catch (Exception e) {
            System.err.println("Error processing webhook: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "Failed to process webhook"));
        }
    }

    @PostMapping("/transfer/initiate")
    public ResponseEntity<?> initiateTransfer(@RequestBody Map<String, String> request) {
        String originalCallControlId = request.get("original_call_control_id");

        if (originalCallControlId == null || originalCallControlId.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: original_call_control_id"));
        }

        try {
            Map<String, String> result = warmTransferService.initiateAgentCall(originalCallControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/transfer/complete")
    public ResponseEntity<?> completeTransfer(@RequestBody Map<String, String> request) {
        String originalCallControlId = request.get("original_call_control_id");
        String agentCallControlId = request.get("agent_call_control_id");

        if (originalCallControlId == null || originalCallControlId.isEmpty() ||
            agentCallControlId == null || agentCallControlId.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required fields: original_call_control_id, agent_call_control_id"));
        }

        try {
            Map<String, String> result = warmTransferService.completeTransfer(originalCallControlId, agentCallControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/hangup")
    public ResponseEntity<?> hangupCall(@RequestBody Map<String, String> request) {
        String callControlId = request.get("call_control_id");

        if (callControlId == null || callControlId.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: call_control_id"));
        }

        try {
            Map<String, String> result = warmTransferService.hangupCall(callControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    private ResponseEntity<?> handleApiException(ApiException e) {
        if (e.getMessage().contains("401") || e.getMessage().contains("Unauthorized")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } else if (e.getMessage().contains("429") || e.getMessage().contains("Rate limit")) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } else if (e.getMessage().contains("503") || e.getMessage().contains("Service unavailable")) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Network error connecting to Telnyx"));
        } else {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}

// src/main/java/com/telnyx/WarmTransferApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class WarmTransferApplication {

    public static void main(String[] args) {
        SpringApplication.run(WarmTransferApplication.class, args);
    }
}
