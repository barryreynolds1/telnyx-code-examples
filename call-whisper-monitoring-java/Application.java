// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx</groupId>
    <artifactId>whisper-prompt-app</artifactId>
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
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
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
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE
WEBHOOK_URL=https://your-domain.com/webhooks/call

// src/main/java/com/telnyx/whisper/WhisperPromptApplication.java
package com.telnyx.whisper;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class WhisperPromptApplication {
    public static void main(String[] args) {
        SpringApplication.run(WhisperPromptApplication.class, args);
    }
}

// src/main/java/com/telnyx/whisper/config/TelnyxConfig.java
package com.telnyx.whisper.config;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {
    
    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}

// src/main/java/com/telnyx/whisper/service/WhisperPromptService.java
package com.telnyx.whisper.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.APIConnectionException;
import com.telnyx.exception.APIException;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.model.CallDialResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class WhisperPromptService {
    
    private final TelnyxClient telnyxClient;
    
    @Value("${TELNYX_PHONE_NUMBER}")
    private String fromNumber;
    
    @Value("${TELNYX_CONNECTION_ID}")
    private String connectionId;
    
    @Autowired
    public WhisperPromptService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }
    
    /**
     * Initiate an outbound call with a whisper prompt.
     * The whisper prompt is played to the caller before the call connects.
     * 
     * @param toNumber Recipient phone number in E.164 format (e.g., +15559876543)
     * @param whisperText Text to be spoken as the whisper prompt
     * @return Map containing call_control_id and other call metadata
     * @throws IllegalArgumentException if phone number format is invalid
     */
    public Map<String, Object> initiateCallWithWhisper(String toNumber, String whisperText) 
            throws AuthenticationException, APIException, APIConnectionException {
        
        // Validate E.164 format to prevent API errors
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15559876543)"
            );
        }
        
        if (whisperText == null || whisperText.trim().isEmpty()) {
            throw new IllegalArgumentException("Whisper text cannot be empty");
        }
        
        // Build request parameters for call initiation
        Map<String, Object> params = new HashMap<>();
        params.put("from_", fromNumber);
        params.put("to", toNumber);
        params.put("connection_id", connectionId);
        params.put("custom_headers", new HashMap<String, String>() {{
            put("X-Whisper-Prompt", whisperText);
        }});
        
        // Initiate the call via Telnyx API
        // The call_control_id is returned in the response and used for subsequent actions
        CallDialResponse response = telnyxClient.calls().dial(params);
        
        // Extract serializable data — SDK objects are NOT JSON-serializable
        return Map.of(
            "call_control_id", response.getData().getCallControlId(),
            "from", fromNumber,
            "to", toNumber,
            "state", response.getData().getState(),
            "whisper_prompt", whisperText
        );
    }
}

// src/main/java/com/telnyx/whisper/controller/CallController.java
package com.telnyx.whisper.controller;

import com.telnyx.exception.APIConnectionException;
import com.telnyx.exception.APIException;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.whisper.service.WhisperPromptService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/calls")
public class CallController {
    
    private final WhisperPromptService whisperPromptService;
    
    @Autowired
    public CallController(WhisperPromptService whisperPromptService) {
        this.whisperPromptService = whisperPromptService;
    }
    
    /**
     * POST /api/calls/initiate-with-whisper
     * Initiates an outbound call with a whisper prompt.
     * 
     * Request body:
     * {
     *   "to": "+15559876543",
     *   "whisper_text": "This is a call from Acme Corp. Press 1 to accept."
     * }
     */
    @PostMapping("/initiate-with-whisper")
    public ResponseEntity<?> initiateCallWithWhisper(@RequestBody Map<String, String> request) {
        String toNumber = request.get("to");
        String whisperText = request.get("whisper_text");
        
        // Validate request payload
        if (toNumber == null || toNumber.isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Missing required field: 'to'"));
        }
        
        if (whisperText == null || whisperText.isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Missing required field: 'whisper_text'"));
        }
        
        try {
            Map<String, Object> result = whisperPromptService.initiateCallWithWhisper(
                toNumber, 
                whisperText
            );
            return ResponseEntity.ok(result);
            
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid API key"));
        } catch (APIException e) {
            // Handle rate limiting and other API errors
            if (e.getMessage().contains("429")) {
                return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
            }
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Map.of("error", e.getMessage()));
        } catch (APIConnectionException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "Network error connecting to Telnyx"));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", e.getMessage()));
        }
    }
}

// src/main/java/com/telnyx/whisper/controller/WebhookController.java
package com.telnyx.whisper.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/webhooks")
public class WebhookController {
    
    /**
     * POST /webhooks/call
     * Receives call control events from Telnyx.
     * Events include: call.initiated, call.answered, call.hangup, etc.
     */
    @PostMapping("/call")
    public ResponseEntity<?> handleCallEvent(@RequestBody Map<String, Object> payload) {
        // Extract event type and call control ID
        String eventType = (String) payload.get("event_type");
        Map<String, Object> data = (Map<String, Object>) payload.get("data");
        
        if (data == null) {
            return ResponseEntity.ok(Map.of("status", "received"));
        }
        
        String callControlId = (String) data.get("call_control_id");
        
        // Log and handle different event types
        switch (eventType) {
            case "call.initiated":
                handleCallInitiated(callControlId, data);
                break;
            case "call.answered":
                handleCallAnswered(callControlId, data);
                break;
            case "call.hangup":
                handleCallHangup(callControlId, data);
                break;
            default:
                System.out.println("Unhandled event type: " + eventType);
        }
        
        // Always return 200 OK to acknowledge receipt
        return ResponseEntity.ok(Map.of("status", "received"));
    }
    
    private void handleCallInitiated(String callControlId, Map<String, Object> data) {
        System.out.println("Call initiated: " + callControlId);
        System.out.println("From: " + data.get("from"));
        System.out.println("To: " + data.get("to"));
    }
    
    private void handleCallAnswered(String callControlId, Map<String, Object> data) {
        System.out.println("Call answered: " + callControlId);
    }
    
    private void handleCallHangup(String callControlId, Map<String, Object> data) {
        System.out.println("Call ended: " + callControlId);
        System.out.println("Hangup reason: " + data.get("hangup_reason"));
    }
}
