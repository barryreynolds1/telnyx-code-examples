// src/main/java/com/telnyx/MmsReceiverApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class MmsReceiverApplication {
    public static void main(String[] args) {
        SpringApplication.run(MmsReceiverApplication.class, args);
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

// src/main/java/com/telnyx/model/MmsMessage.java
package com.telnyx.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class MmsMessage {
    
    @JsonProperty("data")
    private MessageData data;
    
    @JsonProperty("meta")
    private Map<String, Object> meta;
    
    public static class MessageData {
        @JsonProperty("id")
        private String id;
        
        @JsonProperty("type")
        private String type;
        
        @JsonProperty("direction")
        private String direction;
        
        @JsonProperty("from")
        private PhoneNumber from;
        
        @JsonProperty("to")
        private List<PhoneNumber> to;
        
        @JsonProperty("text")
        private String text;
        
        @JsonProperty("media")
        private List<MediaItem> media;
        
        @JsonProperty("received_at")
        private String receivedAt;
        
        public String getId() { return id; }
        public String getType() { return type; }
        public String getDirection() { return direction; }
        public PhoneNumber getFrom() { return from; }
        public List<PhoneNumber> getTo() { return to; }
        public String getText() { return text; }
        public List<MediaItem> getMedia() { return media; }
        public String getReceivedAt() { return receivedAt; }
    }
    
    public static class PhoneNumber {
        @JsonProperty("phone_number")
        private String phoneNumber;
        
        public String getPhoneNumber() { return phoneNumber; }
    }
    
    public static class MediaItem {
        @JsonProperty("url")
        private String url;
        
        @JsonProperty("content_type")
        private String contentType;
        
        @JsonProperty("size")
        private Long size;
        
        public String getUrl() { return url; }
        public String getContentType() { return contentType; }
        public Long getSize() { return size; }
    }
    
    public MessageData getData() { return data; }
    public Map<String, Object> getMeta() { return meta; }
}

// src/main/java/com/telnyx/service/MmsService.java
package com.telnyx.service;

import com.telnyx.model.MmsMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

@Service
public class MmsService {
    
    private static final Logger logger = LoggerFactory.getLogger(MmsService.class);
    
    public Map<String, Object> processMmsMessage(MmsMessage mmsMessage) {
        MmsMessage.MessageData data = mmsMessage.getData();
        
        if (data == null || data.getId() == null) {
            throw new IllegalArgumentException("Invalid MMS payload: missing message data or ID");
        }
        
        logger.info("Received MMS message: id={}, from={}, direction={}", 
            data.getId(),
            data.getFrom() != null ? data.getFrom().getPhoneNumber() : "unknown",
            data.getDirection()
        );
        
        Map<String, Object> mediaInfo = new HashMap<>();
        if (data.getMedia() != null && !data.getMedia().isEmpty()) {
            data.getMedia().forEach(media -> {
                logger.info("Media attachment: url={}, type={}, size={}", 
                    media.getUrl(), 
                    media.getContentType(), 
                    media.getSize()
                );
            });
            mediaInfo.put("count", data.getMedia().size());
            mediaInfo.put("attachments", data.getMedia().stream()
                .map(m -> Map.of(
                    "url", m.getUrl(),
                    "content_type", m.getContentType(),
                    "size", m.getSize()
                ))
                .toList()
            );
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("message_id", data.getId());
        result.put("from", data.getFrom() != null ? data.getFrom().getPhoneNumber() : null);
        result.put("to", data.getTo() != null ? 
            data.getTo().stream().map(MmsMessage.PhoneNumber::getPhoneNumber).toList() : null);
        result.put("text", data.getText());
        result.put("direction", data.getDirection());
        result.put("received_at", data.getReceivedAt());
        result.put("media", mediaInfo);
        
        return result;
    }
}

// src/main/java/com/telnyx/controller/WebhookController.java
package com.telnyx.controller;

import com.telnyx.model.MmsMessage;
import com.telnyx.service.MmsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/webhooks")
public class WebhookController {
    
    private static final Logger logger = LoggerFactory.getLogger(WebhookController.class);
    
    @Autowired
    private MmsService mmsService;
    
    @PostMapping("/message")
    public ResponseEntity<Map<String, Object>> handleMmsWebhook(@RequestBody MmsMessage mmsMessage) {
        try {
            if (mmsMessage == null || mmsMessage.getData() == null) {
                logger.warn("Received invalid webhook payload");
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Invalid webhook payload"));
            }
            
            String direction = mmsMessage.getData().getDirection();
            if (!"inbound".equals(direction)) {
                logger.debug("Ignoring non-inbound message: direction={}", direction);
                return ResponseEntity.ok(Map.of("status", "ignored"));
            }
            
            Map<String, Object> processedMessage = mmsService.processMmsMessage(mmsMessage);
            
            logger.info("Successfully processed MMS message: {}", processedMessage.get("message_id"));
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "received");
            response.put("message", processedMessage);
            
            return ResponseEntity.ok(response);
            
        } catch (IllegalArgumentException e) {
            logger.error("Validation error: {}", e.getMessage());
            return ResponseEntity.badRequest()
                .body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            logger.error("Unexpected error processing webhook", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Internal server error"));
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "healthy"));
    }
}

// src/main/resources/application.properties
spring.application.name=mms-receiver
server.port=8080
logging.level.root=INFO
logging.level.com.telnyx=DEBUG

telnyx.api.key=${TELNYX_API_KEY}
telnyx.webhook.secret=${TELNYX_WEBHOOK_SECRET:}
