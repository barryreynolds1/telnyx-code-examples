// src/main/java/com/telnyx/SmsWebhookApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SmsWebhookApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmsWebhookApplication.class, args);
    }
}

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

// src/main/java/com/telnyx/model/SmsWebhookPayload.java
package com.telnyx.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class SmsWebhookPayload {
    
    @JsonProperty("data")
    private WebhookData data;
    
    @JsonProperty("meta")
    private Map<String, Object> meta;
    
    public static class WebhookData {
        @JsonProperty("id")
        private String id;
        
        @JsonProperty("type")
        private String type;
        
        @JsonProperty("attributes")
        private MessageAttributes attributes;
        
        public String getId() {
            return id;
        }
        
        public void setId(String id) {
            this.id = id;
        }
        
        public String getType() {
            return type;
        }
        
        public void setType(String type) {
            this.type = type;
        }
        
        public MessageAttributes getAttributes() {
            return attributes;
        }
        
        public void setAttributes(MessageAttributes attributes) {
            this.attributes = attributes;
        }
    }
    
    public static class MessageAttributes {
        @JsonProperty("from")
        private String from;
        
        @JsonProperty("to")
        private List<String> to;
        
        @JsonProperty("text")
        private String text;
        
        @JsonProperty("direction")
        private String direction;
        
        @JsonProperty("received_at")
        private String receivedAt;
        
        public String getFrom() {
            return from;
        }
        
        public void setFrom(String from) {
            this.from = from;
        }
        
        public List<String> getTo() {
            return to;
        }
        
        public void setTo(List<String> to) {
            this.to = to;
        }
        
        public String getText() {
            return text;
        }
        
        public void setText(String text) {
            this.text = text;
        }
        
        public String getDirection() {
            return direction;
        }
        
        public void setDirection(String direction) {
            this.direction = direction;
        }
        
        public String getReceivedAt() {
            return receivedAt;
        }
        
        public void setReceivedAt(String receivedAt) {
            this.receivedAt = receivedAt;
        }
    }
    
    public WebhookData getData() {
        return data;
    }
    
    public void setData(WebhookData data) {
        this.data = data;
    }
    
    public Map<String, Object> getMeta() {
        return meta;
    }
    
    public void setMeta(Map<String, Object> meta) {
        this.meta = meta;
    }
}

// src/main/java/com/telnyx/controller/SmsWebhookController.java
package com.telnyx.controller;

import com.telnyx.model.SmsWebhookPayload;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/webhooks")
public class SmsWebhookController {
    
    private static final Logger logger = LoggerFactory.getLogger(SmsWebhookController.class);
    
    @PostMapping("/sms")
    public ResponseEntity<Map<String, Object>> receiveSms(@RequestBody SmsWebhookPayload payload) {
        try {
            if (payload == null || payload.getData() == null) {
                logger.warn("Received invalid webhook payload");
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Invalid webhook payload"));
            }
            
            SmsWebhookPayload.WebhookData data = payload.getData();
            SmsWebhookPayload.MessageAttributes attributes = data.getAttributes();
            
            logger.info("Received SMS webhook - ID: {}, From: {}, To: {}, Direction: {}",
                data.getId(),
                attributes.getFrom(),
                attributes.getTo(),
                attributes.getDirection());
            
            if ("inbound".equals(attributes.getDirection())) {
                logger.info("Inbound SMS from {} with text: {}",
                    attributes.getFrom(),
                    attributes.getText());
            }
            
            return ResponseEntity.ok(Map.of(
                "status", "received",
                "message_id", data.getId()
            ));
            
        } catch (Exception e) {
            logger.error("Error processing SMS webhook", e);
            return ResponseEntity.status(500)
                .body(Map.of("error", "Internal server error"));
        }
    }
}

// src/main/resources/application.properties
server.port=8080
spring.application.name=sms-webhook-receiver
telnyx.api.key=${TELNYX_API_KEY}
telnyx.webhook.secret=${TELNYX_WEBHOOK_SECRET}

// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx</groupId>
    <artifactId>sms-webhook-receiver</artifactId>
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
