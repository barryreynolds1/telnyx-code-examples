// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx.sip</groupId>
    <artifactId>sip-trunking-setup</artifactId>
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
spring.application.name=sip-trunking-setup
server.port=8080
server.servlet.context-path=/api

// src/main/java/com/telnyx/sip/SipTrunkingApplication.java
package com.telnyx.sip;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SipTrunkingApplication {

    public static void main(String[] args) {
        SpringApplication.run(SipTrunkingApplication.class, args);
    }
}

// src/main/java/com/telnyx/sip/config/TelnyxConfig.java
package com.telnyx.sip.config;

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

// src/main/java/com/telnyx/sip/service/SipConnectionService.java
package com.telnyx.sip.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.sip.SipConnection;
import com.telnyx.model.sip.SipConnectionCreateRequest;
import com.telnyx.model.sip.SipConnectionListResponse;
import com.telnyx.model.sip.SipConnectionResponse;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SipConnectionService {

    private final TelnyxClient telnyxClient;

    public SipConnectionService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public Map<String, Object> createSipConnection(
            String name,
            String username,
            String password,
            String sipAddress) throws TelnyxException {

        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Connection name is required");
        }
        if (username == null || username.isBlank()) {
            throw new IllegalArgumentException("Username is required");
        }
        if (password == null || password.isBlank()) {
            throw new IllegalArgumentException("Password is required");
        }
        if (sipAddress == null || sipAddress.isBlank()) {
            throw new IllegalArgumentException("SIP address is required");
        }

        SipConnectionCreateRequest request = new SipConnectionCreateRequest();
        request.setName(name);
        request.setUsername(username);
        request.setPassword(password);
        request.setSipAddress(sipAddress);

        SipConnectionResponse response = telnyxClient.sipConnections().create(request);
        return extractSipConnectionData(response.getData());
    }

    public Map<String, Object> getSipConnection(String connectionId) throws TelnyxException {
        if (connectionId == null || connectionId.isBlank()) {
            throw new IllegalArgumentException("Connection ID is required");
        }

        SipConnectionResponse response = telnyxClient.sipConnections().retrieve(connectionId);
        return extractSipConnectionData(response.getData());
    }

    public List<Map<String, Object>> listSipConnections(Integer pageSize) throws TelnyxException {
        SipConnectionListResponse response = telnyxClient.sipConnections()
                .list(pageSize != null ? pageSize : 20);

        return response.getData().stream()
                .map(this::extractSipConnectionData)
                .toList();
    }

    private Map<String, Object> extractSipConnectionData(SipConnection connection) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", connection.getId());
        data.put("name", connection.getName());
        data.put("username", connection.getUsername());
        data.put("sipAddress", connection.getSipAddress());
        data.put("createdAt", connection.getCreatedAt());
        data.put("updatedAt", connection.getUpdatedAt());
        return data;
    }
}

// src/main/java/com/telnyx/sip/controller/SipConnectionController.java
package com.telnyx.sip.controller;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.sip.service.SipConnectionService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/sip-connections")
public class SipConnectionController {

    private final SipConnectionService sipConnectionService;

    public SipConnectionController(SipConnectionService sipConnectionService) {
        this.sipConnectionService = sipConnectionService;
    }

    @PostMapping
    public ResponseEntity<?> createSipConnection(
            @RequestBody Map<String, String> request) {

        try {
            String name = request.get("name");
            String username = request.get("username");
            String password = request.get("password");
            String sipAddress = request.get("sip_address");

            Map<String, Object> result = sipConnectionService.createSipConnection(
                    name, username, password, sipAddress);

            return ResponseEntity.status(HttpStatus.CREATED).body(result);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getSipConnection(@PathVariable String id) {
        try {
            Map<String, Object> result = sipConnectionService.getSipConnection(id);
            return ResponseEntity.ok(result);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping
    public ResponseEntity<?> listSipConnections(
            @RequestParam(required = false) Integer pageSize) {

        try {
            List<Map<String, Object>> result = sipConnectionService.listSipConnections(pageSize);
            return ResponseEntity.ok(Map.of("data", result));

        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));
        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } catch (TelnyxException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}
