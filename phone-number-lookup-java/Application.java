// src/main/java/com/telnyx/NumberLookupApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class NumberLookupApplication {
    public static void main(String[] args) {
        SpringApplication.run(NumberLookupApplication.class, args);
    }
}

// src/main/java/com/telnyx/config/TelnyxConfig.java
package com.telnyx.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "telnyx")
public class TelnyxConfig {
    private String apiKey;

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }
}

// src/main/java/com/telnyx/config/TelnyxClientConfig.java
package com.telnyx.config;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxClientConfig {
    @Bean
    public TelnyxClient telnyxClient(TelnyxConfig telnyxConfig) {
        return TelnyxOkHttpClient.fromEnv();
    }
}

// src/main/java/com/telnyx/service/NumberLookupService.java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.APIConnectionException;
import com.telnyx.exception.APIException;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.model.numberlookup.NumberLookup;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class NumberLookupService {
    private final TelnyxClient telnyxClient;

    public NumberLookupService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public Map<String, Object> lookupNumber(String phoneNumber) {
        if (phoneNumber == null || !phoneNumber.startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15551234567)"
            );
        }

        NumberLookup response = telnyxClient.numberLookup().retrieve(phoneNumber);

        Map<String, Object> result = new HashMap<>();
        result.put("phone_number", response.getPhoneNumber());
        result.put("country_code", response.getCountryCode());
        result.put("national_format", response.getNationalFormat());
        result.put("carrier_name", response.getCarrierName());
        result.put("carrier_type", response.getCarrierType());
        result.put("line_type", response.getLineType());
        result.put("is_valid", response.getIsValid());
        result.put("portability_status", response.getPortabilityStatus());

        return result;
    }
}

// src/main/java/com/telnyx/controller/NumberLookupController.java
package com.telnyx.controller;

import com.telnyx.exception.APIConnectionException;
import com.telnyx.exception.APIException;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.service.NumberLookupService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/number-lookup")
public class NumberLookupController {
    private final NumberLookupService numberLookupService;

    public NumberLookupController(NumberLookupService numberLookupService) {
        this.numberLookupService = numberLookupService;
    }

    @PostMapping("/lookup")
    public ResponseEntity<Map<String, Object>> lookup(@RequestBody Map<String, String> request) {
        String phoneNumber = request.get("phone_number");

        if (phoneNumber == null || phoneNumber.isEmpty()) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Missing required field: 'phone_number'");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            Map<String, Object> result = numberLookupService.lookupNumber(phoneNumber);
            return ResponseEntity.ok(result);
        } catch (AuthenticationException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        } catch (RateLimitException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Rate limit exceeded. Please slow down.");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
        } catch (APIException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("status_code", e.getStatusCode());
            return ResponseEntity.status(e.getStatusCode()).body(error);
        } catch (APIConnectionException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Network error connecting to Telnyx");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/lookup")
    public ResponseEntity<Map<String, Object>> lookupGet(
            @RequestParam(name = "phone_number") String phoneNumber) {
        if (phoneNumber == null || phoneNumber.isEmpty()) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Missing required parameter: 'phone_number'");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            Map<String, Object> result = numberLookupService.lookupNumber(phoneNumber);
            return ResponseEntity.ok(result);
        } catch (AuthenticationException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        } catch (RateLimitException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Rate limit exceeded. Please slow down.");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
        } catch (APIException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("status_code", e.getStatusCode());
            return ResponseEntity.status(e.getStatusCode()).body(error);
        } catch (APIConnectionException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Network error connecting to Telnyx");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
}

// src/main/resources/application.yml
spring:
  application:
    name: number-lookup-service
  profiles:
    active: dev

server:
  port: 8080
  servlet:
    context-path: /api

telnyx:
  api-key: ${TELNYX_API_KEY}
