// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx</groupId>
    <artifactId>sms-notifications</artifactId>
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
spring.application.name=sms-notifications
server.port=8080
telnyx.api.key=${TELNYX_API_KEY}
telnyx.phone.number=${TELNYX_PHONE_NUMBER}

// src/main/java/com/telnyx/SmsNotificationsApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SmsNotificationsApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(SmsNotificationsApplication.class, args);
    }
}

// src/main/java/com/telnyx/config/TelnyxConfig.java
package com.telnyx.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {
    
    @Value("${telnyx.api.key}")
    private String apiKey;
    
    @Value("${telnyx.phone.number}")
    private String phoneNumber;
    
    public String getApiKey() {
        return apiKey;
    }
    
    public String getPhoneNumber() {
        return phoneNumber;
    }
}

// src/main/java/com/telnyx/service/SmsNotificationService.java
package com.telnyx.service;

import com.telnyx.config.TelnyxConfig;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.Message;
import com.telnyx.net.TelnyxClient;
import com.telnyx.net.TelnyxOkHttpClient;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class SmsNotificationService {
    
    private final TelnyxConfig telnyxConfig;
    private final TelnyxClient client;
    
    public SmsNotificationService(TelnyxConfig telnyxConfig) {
        this.telnyxConfig = telnyxConfig;
        this.client = TelnyxOkHttpClient.fromEnv();
    }
    
    /**
     * Send SMS notification to a single recipient.
     * Validates phone number format and returns serializable response data.
     */
    public Map<String, Object> sendNotification(String toNumber, String message) 
            throws TelnyxException {
        
        String fromNumber = telnyxConfig.getPhoneNumber();
        
        if (fromNumber == null || fromNumber.isEmpty()) {
            throw new IllegalArgumentException("TELNYX_PHONE_NUMBER not configured");
        }
        
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15551234567)"
            );
        }
        
        if (message == null || message.trim().isEmpty()) {
            throw new IllegalArgumentException("Message text cannot be empty");
        }
        
        try {
            Message response = client.messages.create(
                new HashMap<String, Object>() {{
                    put("from", fromNumber);
                    put("to", toNumber);
                    put("text", message);
                }}
            );
            
            Map<String, Object> result = new HashMap<>();
            result.put("message_id", response.getId());
            result.put("status", response.getTo() != null && !response.getTo().isEmpty() 
                ? response.getTo().get(0).getStatus() 
                : "unknown");
            result.put("from", fromNumber);
            result.put("to", toNumber);
            result.put("direction", response.getDirection());
            
            return result;
            
        } catch (TelnyxException e) {
            throw e;
        }
    }
}

// src/main/java/com/telnyx/controller/SmsNotificationController.java
package com.telnyx.controller;

import com.telnyx.exception.TelnyxException;
import com.telnyx.service.SmsNotificationService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/sms")
public class SmsNotificationController {
    
    private final SmsNotificationService smsService;
    
    public SmsNotificationController(SmsNotificationService smsService) {
        this.smsService = smsService;
    }
    
    /**
     * POST /api/sms/send - Send a single SMS notification.
     * Request body: {"to": "+15559876543", "message": "Hello from Telnyx!"}
     */
    @PostMapping("/send")
    public ResponseEntity<Map<String, Object>> sendNotification(
            @RequestBody Map<String, String> request) {
        
        String toNumber = request.get("to");
        String message = request.get("message");
        
        if (toNumber == null || toNumber.isEmpty()) {
            return ResponseEntity.badRequest().body(
                Map.of("error", "Missing required field: 'to'")
            );
        }
        
        if (message == null || message.isEmpty()) {
            return ResponseEntity.badRequest().body(
                Map.of("error", "Missing required field: 'message'")
            );
        }
        
        try {
            Map<String, Object> result = smsService.sendNotification(toNumber, message);
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(
                Map.of("error", e.getMessage())
            );
        } catch (TelnyxException e) {
            return handleTelnyxException(e);
        }
    }
    
    /**
     * Global exception handler for Telnyx API errors.
     * Maps SDK exceptions to appropriate HTTP status codes.
     */
    private ResponseEntity<Map<String, Object>> handleTelnyxException(TelnyxException e) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("error", e.getMessage());
        
        if (e instanceof com.telnyx.exception.AuthenticationException) {
            errorResponse.put("error_type", "authentication_error");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorResponse);
        } else if (e instanceof com.telnyx.exception.RateLimitException) {
            errorResponse.put("error_type", "rate_limit_error");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(errorResponse);
        } else if (e instanceof com.telnyx.exception.APIConnectionException) {
            errorResponse.put("error_type", "connection_error");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(errorResponse);
        } else if (e instanceof com.telnyx.exception.APIStatusException) {
            com.telnyx.exception.APIStatusException statusException = 
                (com.telnyx.exception.APIStatusException) e;
            errorResponse.put("status_code", statusException.getStatusCode());
            return ResponseEntity.status(statusException.getStatusCode()).body(errorResponse);
        }
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
    }
}
