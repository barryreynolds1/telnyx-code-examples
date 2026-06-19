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
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.AiAssistant;
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

    public Map<String, Object> chatWithAssistant(String userMessage) {
        if (userMessage == null || userMessage.trim().isEmpty()) {
            throw new IllegalArgumentException("Message cannot be empty");
        }

        ChatResponse response = telnyxClient.aiAssistants().chat(
            assistantId,
            userMessage
        );

        Map<String, Object> result = new HashMap<>();
        result.put("assistant_id", assistantId);
        result.put("user_message", userMessage);
        result.put("assistant_response", response.getData().getMessage());
        result.put("conversation_id", response.getData().getConversationId());
        result.put("tokens_used", response.getData().getTokensUsed());

        return result;
    }

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

// src/main/java/com/telnyx/controller/ChatController.java
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

    @PostMapping("/message")
    public ResponseEntity<?> sendMessage(@RequestBody ChatRequest request) {
        if (request == null || request.getMessage() == null) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Request body with 'message' field is required");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            Map<String, Object> response = aiAssistantService.chatWithAssistant(request.getMessage());
            return ResponseEntity.ok(response);

        } catch (AuthenticationException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (RateLimitException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Rate limit exceeded. Please slow down.");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);

        } catch (TelnyxException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);

        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

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

// src/main/java/com/telnyx/AiAssistantChatApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AiAssistantChatApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiAssistantChatApplication.class, args);
    }
}

// src/main/resources/application.properties
spring.application.name=ai-assistant-chat
server.port=8080
telnyx.api.key=${TELNYX_API_KEY}
telnyx.assistant.id=${TELNYX_ASSISTANT_ID}
