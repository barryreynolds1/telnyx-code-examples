// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx.sip</groupId>
    <artifactId>sip-registration</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>SIP Registration</name>
    <description>Spring Boot application for SIP connection registration with Telnyx</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>11</java.version>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>

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
            <groupId>io.github.cdimascio</groupId>
            <artifactId>dotenv-java</artifactId>
            <version>3.0.0</version>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
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

// src/main/java/com/telnyx/sip/SipRegistrationApplication.java
package com.telnyx.sip;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SipRegistrationApplication {
    public static void main(String[] args) {
        SpringApplication.run(SipRegistrationApplication.class, args);
    }
}

// src/main/java/com/telnyx/sip/config/TelnyxConfig.java
package com.telnyx.sip.config;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TelnyxConfig {
    static {
        Dotenv dotenv = Dotenv.load();
    }

    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}

// src/main/java/com/telnyx/sip/service/SipRegistrationService.java
package com.telnyx.sip.service;

import com.telnyx.TelnyxClient;
import com.telnyx.model.sip.SipConnection;
import com.telnyx.model.sip.SipConnectionCreateRequest;
import com.telnyx.model.sip.SipConnectionResponse;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class SipRegistrationService {
    private final TelnyxClient telnyxClient;

    public SipRegistrationService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public Map<String, Object> registerSipConnection(
            String connectionName,
            String username,
            String password,
            String sipEndpoint) {

        if (connectionName == null || connectionName.trim().isEmpty()) {
            throw new IllegalArgumentException("Connection name is required");
        }
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("SIP username is required");
        }
        if (password == null || password.trim().isEmpty()) {
            throw new IllegalArgumentException("SIP password is required");
        }
        if (sipEndpoint == null || sipEndpoint.trim().isEmpty()) {
            throw new IllegalArgumentException("SIP endpoint is required");
        }

        SipConnectionCreateRequest request = new SipConnectionCreateRequest()
                .setName(connectionName)
                .setUsername(username)
                .setPassword(password)
                .setSipEndpoint(sipEndpoint)
                .setAuthType("credential");

        SipConnectionResponse response = telnyxClient.sipConnections().create(request);
        return extractConnectionData(response.getData());
    }

    public Map<String, Object> getSipConnection(String connectionId) {
        if (connectionId == null || connectionId.trim().isEmpty()) {
            throw new IllegalArgumentException("Connection ID is required");
        }

        SipConnectionResponse response = telnyxClient.sipConnections().retrieve(connectionId);
        return extractConnectionData(response.getData());
    }

    private Map<String, Object> extractConnectionData(SipConnection connection) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", connection.getId());
        data.put("name", connection.getName());
        data.put("username", connection.getUsername());
        data.put("sip_endpoint", connection.getSipEndpoint());
        data.put("auth_type", connection.getAuthType());
        data.put("created_at", connection.getCreatedAt());
        data.put("updated_at", connection.getUpdatedAt());
        return data;
    }
}

// src/main/java/com/telnyx/sip/controller/SipRegistrationController.java
package com.telnyx.sip.controller;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.sip.service.SipRegistrationService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/sip")
public class SipRegistrationController {
    private final SipRegistrationService sipRegistrationService;

    public SipRegistrationController(SipRegistrationService sipRegistrationService) {
        this.sipRegistrationService = sipRegistrationService;
    }

    @PostMapping("/register")
    public ResponseEntity<?> registerSipConnection(@RequestBody SipRegistrationRequest request) {
        if (request == null) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Request body required"));
        }

        if (request.getConnectionName() == null || request.getConnectionName().trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: 'connectionName'"));
        }

        if (request.getUsername() == null || request.getUsername().trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: 'username'"));
        }

        if (request.getPassword() == null || request.getPassword().trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: 'password'"));
        }

        if (request.getSipEndpoint() == null || request.getSipEndpoint().trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing required field: 'sipEndpoint'"));
        }

        try {
            Map<String, Object> result = sipRegistrationService.registerSipConnection(
                    request.getConnectionName(),
                    request.getUsername(),
                    request.getPassword(),
                    request.getSipEndpoint()
            );
            return ResponseEntity.status(HttpStatus.CREATED).body(result);

        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));

        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));

        } catch (TelnyxException e) {
            int statusCode = e.getStatusCode() != null ? e.getStatusCode() : 500;
            return ResponseEntity.status(statusCode)
                    .body(Map.of("error", e.getMessage(), "status_code", statusCode));

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/connections/{connectionId}")
    public ResponseEntity<?> getSipConnection(@PathVariable String connectionId) {
        if (connectionId == null || connectionId.trim().isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Connection ID is required"));
        }

        try {
            Map<String, Object> result = sipRegistrationService.getSipConnection(connectionId);
            return ResponseEntity.ok(result);

        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid API key"));

        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please slow down."));

        } catch (TelnyxException e) {
            int statusCode = e.getStatusCode() != null ? e.getStatusCode() : 500;
            return ResponseEntity.status(statusCode)
                    .body(Map.of("error", e.getMessage(), "status_code", statusCode));

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        }
    }

    public static class SipRegistrationRequest {
        private String connectionName;
        private String username;
        private String password;
        private String sipEndpoint;

        public String getConnectionName() {
            return connectionName;
        }

        public void setConnectionName(String connectionName) {
            this.connectionName = connectionName;
        }

        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getSipEndpoint() {
            return sipEndpoint;
        }

        public void setSipEndpoint(String sipEndpoint) {
            this.sipEndpoint = sipEndpoint;
        }
    }
}

// .env
TELNYX_API_KEY=YOUR_API_KEY_HERE
SIP_USERNAME=your_sip_username
SIP_PASSWORD=your_sip_password
SIP_ENDPOINT=sip.example.com:5060

// src/main/resources/application.properties
spring.application.name=sip-registration
server.port=8080
