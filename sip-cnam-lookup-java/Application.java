// src/main/java/com/telnyx/CnamLookupApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CnamLookupApplication {
    public static void main(String[] args) {
        SpringApplication.run(CnamLookupApplication.class, args);
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

// src/main/java/com/telnyx/service/CnamLookupService.java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.CnamLookup;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class CnamLookupService {
    private final TelnyxClient telnyxClient;
    
    @Autowired
    public CnamLookupService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }
    
    public Map<String, Object> lookupCnam(String phoneNumber) {
        if (phoneNumber == null || !phoneNumber.startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15551234567)"
            );
        }
        
        CnamLookup response = telnyxClient.cnamLookups().retrieve(phoneNumber);
        
        Map<String, Object> result = new HashMap<>();
        result.put("phone_number", response.getData().getPhoneNumber());
        result.put("caller_name", response.getData().getCallerName());
        result.put("carrier_name", response.getData().getCarrierName());
        result.put("lookup_status", response.getData().getLookupStatus());
        
        return result;
    }
}

// src/main/java/com/telnyx/controller/CnamLookupController.java
package com.telnyx.controller;

import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.service.CnamLookupService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/cnam")
public class CnamLookupController {
    private final CnamLookupService cnamLookupService;
    
    @Autowired
    public CnamLookupController(CnamLookupService cnamLookupService) {
        this.cnamLookupService = cnamLookupService;
    }
    
    @GetMapping("/lookup")
    public ResponseEntity<?> lookupCnam(@RequestParam String phoneNumber) {
        try {
            Map<String, Object> result = cnamLookupService.lookupCnam(phoneNumber);
            return ResponseEntity.ok(result);
            
        } catch (AuthenticationException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Invalid API key");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            
        } catch (RateLimitException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Rate limit exceeded. Please slow down.");
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
            
        } catch (TelnyxException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("status_code", e.getStatusCode());
            return ResponseEntity.status(e.getStatusCode()).body(error);
            
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }
}

// src/main/resources/application.properties
telnyx.api.key=${TELNYX_API_KEY}
server.port=8080

// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.telnyx</groupId>
    <artifactId>cnam-lookup-service</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <name>CNAM Lookup Service</name>
    <description>Spring Boot service for CNAM lookups via Telnyx</description>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/>
    </parent>
    
    <properties>
        <java.version>11</java.version>
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
