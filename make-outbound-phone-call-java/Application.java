// src/main/java/com/telnyx/OutboundCallApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OutboundCallApplication {
    public static void main(String[] args) {
        SpringApplication.run(OutboundCallApplication.class, args);
    }
}

// src/main/java/com/telnyx/config/TelnyxConfig.java
package com.telnyx.config;

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

// src/main/java/com/telnyx/service/CallService.java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
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

    public Map<String, Object> initiateCall(String toNumber) {
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

        CallDialResponse response = telnyxClient.calls().dial(
            fromNumber,
            toNumber,
            connectionId
        );

        Map<String, Object> result = new HashMap<>();
        result.put("call_control_id", response.getData().getCallControlId());
        result.put("from", fromNumber);
        result.put("to", toNumber);
        result.put("state", response.getData().getState());

        return result;
    }
}

// src/main/java/com/telnyx/controller/CallController.java
package com.telnyx.controller;

import com.telnyx.service.CallService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/calls")
public class CallController {

    @Autowired
    private CallService callService;

    @PostMapping("/initiate")
    public ResponseEntity<Map<String, Object>> initiateCall(@RequestBody Map<String, String> request) {
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
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
}

// src/main/java/com/telnyx/exception/GlobalExceptionHandler.java
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

// src/main/resources/application.properties
TELNYX_API_KEY=YOUR_API_KEY_HERE
TELNYX_PHONE_NUMBER=+15551234567
TELNYX_CONNECTION_ID=YOUR_CONNECTION_ID_HERE
server.port=8080
