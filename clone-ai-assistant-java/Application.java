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

// src/main/java/com/telnyx/service/AiAssistantService.java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.model.AiAssistant;
import com.telnyx.model.CloneAssistantRequest;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class AiAssistantService {

    private final TelnyxClient telnyxClient;

    public AiAssistantService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public Map<String, Object> cloneAssistant(String assistantId, Map<String, Object> overrides) {
        AiAssistant original = telnyxClient.aiAssistants().retrieve(assistantId).getData();

        CloneAssistantRequest.Builder requestBuilder = CloneAssistantRequest.builder()
                .name(overrides.getOrDefault("name", original.getName()).toString());

        if (overrides.containsKey("instructions")) {
            requestBuilder.instructions(overrides.get("instructions").toString());
        }
        if (overrides.containsKey("model")) {
            requestBuilder.model(overrides.get("model").toString());
        }

        AiAssistant cloned = telnyxClient.aiAssistants()
                .clone(assistantId, requestBuilder.build())
                .getData();

        return extractAssistantData(cloned);
    }

    private Map<String, Object> extractAssistantData(AiAssistant assistant) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", assistant.getId());
        result.put("name", assistant.getName());
        result.put("model", assistant.getModel());
        result.put("instructions", assistant.getInstructions());
        result.put("enabled_features", assistant.getEnabledFeatures());
        result.put("created_at", assistant.getCreatedAt());
        return result;
    }
}

// src/main/java/com/telnyx/controller/AiAssistantController.java
package com.telnyx.controller;

import com.telnyx.service.AiAssistantService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/assistants")
public class AiAssistantController {

    private final AiAssistantService aiAssistantService;

    public AiAssistantController(AiAssistantService aiAssistantService) {
        this.aiAssistantService = aiAssistantService;
    }

    @PostMapping("/{assistantId}/clone")
    public ResponseEntity<Map<String, Object>> cloneAssistant(
            @PathVariable String assistantId,
            @RequestBody(required = false) Map<String, Object> overrides) {

        if (assistantId == null || assistantId.isBlank()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Assistant ID is required"));
        }

        if (overrides == null) {
            overrides = new HashMap<>();
        }

        try {
            Map<String, Object> clonedAssistant = aiAssistantService.cloneAssistant(assistantId, overrides);
            return ResponseEntity.status(HttpStatus.CREATED).body(clonedAssistant);

        } catch (com.telnyx.AuthenticationError e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));

        } catch (com.telnyx.RateLimitError e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));

        } catch (com.telnyx.APIStatusError e) {
            return ResponseEntity.status(e.getStatusCode())
                    .body(Map.of("error", e.getMessage(), "status_code", e.getStatusCode()));

        } catch (com.telnyx.APIConnectionError e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Network error connecting to Telnyx"));

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Internal server error: " + e.getMessage()));
        }
    }
}

// src/main/java/com/telnyx/AiAssistantClonerApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AiAssistantClonerApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiAssistantClonerApplication.class, args);
    }
}

// src/main/resources/application.properties
spring.application.name=ai-assistant-cloner
server.port=8080
telnyx.api.key=${TELNYX_API_KEY}
