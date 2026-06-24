// src/main/java/com/telnyx/HoldMusicApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class HoldMusicApplication {
    public static void main(String[] args) {
        SpringApplication.run(HoldMusicApplication.class, args);
    }
}

// src/main/java/com/telnyx/config/TelnyxConfig.java
package com.telnyx.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class TelnyxConfig {
    @Value("${telnyx.api.key}")
    public String apiKey;

    @Value("${telnyx.phone.number}")
    public String phoneNumber;

    @Value("${telnyx.connection.id}")
    public String connectionId;

    @Value("${telnyx.hold.music.url}")
    public String holdMusicUrl;

    @Value("${telnyx.webhook.url}")
    public String webhookUrl;
}

// src/main/java/com/telnyx/service/CallControlService.java
package com.telnyx.service;

import com.telnyx.config.TelnyxConfig;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.CallControlResponse;
import com.telnyx.model.CallDialResponse;
import com.telnyx.rest.TelnyxClient;
import com.telnyx.rest.TelnyxOkHttpClient;
import org.springframework.stereotype.Service;

@Service
public class CallControlService {
    private final TelnyxConfig config;
    private final TelnyxClient client;

    public CallControlService(TelnyxConfig config) {
        this.config = config;
        this.client = TelnyxOkHttpClient.fromEnv();
    }

    public String initiateCallWithHoldMusic(String toNumber) throws TelnyxException {
        try {
            CallDialResponse response = client.calls().dial(
                config.phoneNumber,
                toNumber,
                config.connectionId
            );
            return response.getData().getCallControlId();
        } catch (TelnyxException e) {
            throw new RuntimeException("Failed to initiate call: " + e.getMessage(), e);
        }
    }

    public void playHoldMusic(String callControlId) throws TelnyxException {
        try {
            client.calls().actions().speak(
                callControlId,
                config.holdMusicUrl,
                "audio/mpeg"
            );
        } catch (TelnyxException e) {
            throw new RuntimeException("Failed to play hold music: " + e.getMessage(), e);
        }
    }

    public void hangupCall(String callControlId) throws TelnyxException {
        try {
            client.calls().actions().hangup(callControlId);
        } catch (TelnyxException e) {
            throw new RuntimeException("Failed to hangup call: " + e.getMessage(), e);
        }
    }
}

// src/main/java/com/telnyx/controller/CallController.java
package com.telnyx.controller;

import com.telnyx.service.CallControlService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/calls")
public class CallController {
    private final CallControlService callControlService;

    public CallController(CallControlService callControlService) {
        this.callControlService = callControlService;
    }

    @PostMapping("/initiate")
    public ResponseEntity<?> initiateCall(@RequestBody Map<String, String> request) {
        String toNumber = request.get("to");

        if (toNumber == null || toNumber.isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Missing required field: 'to'"));
        }

        if (!toNumber.startsWith("+")) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Phone number must be in E.164 format (e.g., +15551234567)"));
        }

        try {
            String callControlId = callControlService.initiateCallWithHoldMusic(toNumber);
            return ResponseEntity.ok(Map.of(
                "call_control_id", callControlId,
                "status", "initiated",
                "message", "Call initiated. Awaiting answer event."
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500)
                .body(Map.of("error", "Failed to initiate call: " + e.getMessage()));
        }
    }
}

// src/main/java/com/telnyx/controller/CallWebhookController.java
package com.telnyx.controller;

import com.telnyx.service.CallControlService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/webhooks")
public class CallWebhookController {
    private final CallControlService callControlService;

    public CallWebhookController(CallControlService callControlService) {
        this.callControlService = callControlService;
    }

    @PostMapping("/call")
    public ResponseEntity<?> handleCallEvent(@RequestBody Map<String, Object> payload) {
        try {
            String eventType = (String) payload.get("event_type");
            Map<String, Object> data = (Map<String, Object>) payload.get("data");

            if (data == null) {
                return ResponseEntity.ok(Map.of("status", "received"));
            }

            String callControlId = (String) data.get("call_control_id");

            switch (eventType) {
                case "call.answered":
                    callControlService.playHoldMusic(callControlId);
                    return ResponseEntity.ok(Map.of(
                        "status", "hold_music_started",
                        "call_control_id", callControlId
                    ));

                case "call.hangup":
                    return ResponseEntity.ok(Map.of(
                        "status", "call_ended",
                        "call_control_id", callControlId
                    ));

                case "call.initiated":
                    return ResponseEntity.ok(Map.of(
                        "status", "call_initiated",
                        "call_control_id", callControlId
                    ));

                default:
                    return ResponseEntity.ok(Map.of("status", "event_received"));
            }

        } catch (Exception e) {
            System.err.println("Webhook processing error: " + e.getMessage());
            return ResponseEntity.ok(Map.of("status", "error_logged"));
        }
    }
}

// src/main/java/com/telnyx/exception/GlobalExceptionHandler.java
package com.telnyx.exception;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.APIStatusException;
import com.telnyx.exception.APIConnectionException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.util.Map;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<?> handleAuthenticationError(AuthenticationException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
            .body(Map.of("error", "Invalid API key: " + e.getMessage()));
    }

    @ExceptionHandler(RateLimitException.class)
    public ResponseEntity<?> handleRateLimitError(RateLimitException e) {
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
            .body(Map.of("error", "Rate limit exceeded. Please slow down."));
    }

    @ExceptionHandler(APIStatusException.class)
    public ResponseEntity<?> handleAPIStatusError(APIStatusException e) {
        int statusCode = e.getStatusCode();
        return ResponseEntity.status(statusCode)
            .body(Map.of(
                "error", e.getMessage(),
                "status_code", statusCode
            ));
    }

    @ExceptionHandler(APIConnectionException.class)
    public ResponseEntity<?> handleConnectionError(APIConnectionException e) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(Map.of("error", "Network error connecting to Telnyx: " + e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handleGenericError(Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(Map.of("error", "Internal server error: " + e.getMessage()));
    }
}
