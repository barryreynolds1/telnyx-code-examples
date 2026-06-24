// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.telnyx</groupId>
    <artifactId>device-location-service</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

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
spring.application.name=device-location-service
server.port=8080
server.servlet.context-path=/api
telnyx.api.key=${TELNYX_API_KEY}

// src/main/java/com/telnyx/DeviceLocationApplication.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DeviceLocationApplication {
    public static void main(String[] args) {
        SpringApplication.run(DeviceLocationApplication.class, args);
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

// src/main/java/com/telnyx/model/DeviceLocation.java
package com.telnyx.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DeviceLocation {
    @JsonProperty("sim_card_id")
    private String simCardId;

    @JsonProperty("iccid")
    private String iccid;

    @JsonProperty("status")
    private String status;

    @JsonProperty("latitude")
    private Double latitude;

    @JsonProperty("longitude")
    private Double longitude;

    @JsonProperty("accuracy_meters")
    private Integer accuracyMeters;

    @JsonProperty("last_location_update")
    private String lastLocationUpdate;

    @JsonProperty("carrier_name")
    private String carrierName;

    public DeviceLocation() {}

    public DeviceLocation(String simCardId, String iccid, String status) {
        this.simCardId = simCardId;
        this.iccid = iccid;
        this.status = status;
    }

    public String getSimCardId() { return simCardId; }
    public void setSimCardId(String simCardId) { this.simCardId = simCardId; }

    public String getIccid() { return iccid; }
    public void setIccid(String iccid) { this.iccid = iccid; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }

    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }

    public Integer getAccuracyMeters() { return accuracyMeters; }
    public void setAccuracyMeters(Integer accuracyMeters) { this.accuracyMeters = accuracyMeters; }

    public String getLastLocationUpdate() { return lastLocationUpdate; }
    public void setLastLocationUpdate(String lastLocationUpdate) { this.lastLocationUpdate = lastLocationUpdate; }

    public String getCarrierName() { return carrierName; }
    public void setCarrierName(String carrierName) { this.carrierName = carrierName; }
}

// src/main/java/com/telnyx/exception/TelnyxException.java
package com.telnyx.exception;

public class TelnyxException extends Exception {
    public TelnyxException(String message) {
        super(message);
    }

    public TelnyxException(String message, Throwable cause) {
        super(message, cause);
    }
}

// src/main/java/com/telnyx/service/LocationService.java
package com.telnyx.service;

import com.telnyx.TelnyxClient;
import com.telnyx.model.DeviceLocation;
import com.telnyx.exception.TelnyxException;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.APIStatusException;
import com.telnyx.exception.APIConnectionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.ArrayList;
import java.util.List;

@Service
public class LocationService {

    private final TelnyxClient telnyxClient;

    @Autowired
    public LocationService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public List<DeviceLocation> getAllDeviceLocations() throws TelnyxException {
        List<DeviceLocation> locations = new ArrayList<>();

        try {
            var response = telnyxClient.simCards().list();

            if (response.getData() != null) {
                for (var simCard : response.getData()) {
                    DeviceLocation location = new DeviceLocation();
                    location.setSimCardId(simCard.getId());
                    location.setIccid(simCard.getIccid());
                    location.setStatus(simCard.getStatus());

                    if (simCard.getNetworkAccessProfile() != null) {
                        location.setCarrierName(simCard.getNetworkAccessProfile().getName());
                    }

                    location.setLastLocationUpdate(simCard.getUpdatedAt());
                    locations.add(location);
                }
            }

            return locations;

        } catch (AuthenticationException e) {
            throw new TelnyxException("Authentication failed: " + e.getMessage(), e);
        } catch (RateLimitException e) {
            throw new TelnyxException("Rate limit exceeded: " + e.getMessage(), e);
        } catch (APIStatusException e) {
            throw new TelnyxException("API error: " + e.getMessage(), e);
        } catch (APIConnectionException e) {
            throw new TelnyxException("Connection error: " + e.getMessage(), e);
        }
    }

    public DeviceLocation getDeviceLocationBySim(String simCardId) throws TelnyxException {
        try {
            var response = telnyxClient.simCards().retrieve(simCardId);
            var simCard = response.getData();

            DeviceLocation location = new DeviceLocation();
            location.setSimCardId(simCard.getId());
            location.setIccid(simCard.getIccid());
            location.setStatus(simCard.getStatus());
            location.setLastLocationUpdate(simCard.getUpdatedAt());

            if (simCard.getNetworkAccessProfile() != null) {
                location.setCarrierName(simCard.getNetworkAccessProfile().getName());
            }

            return location;

        } catch (AuthenticationException e) {
            throw new TelnyxException("Authentication failed: " + e.getMessage(), e);
        } catch (RateLimitException e) {
            throw new TelnyxException("Rate limit exceeded: " + e.getMessage(), e);
        } catch (APIStatusException e) {
            throw new TelnyxException("API error: " + e.getMessage(), e);
        } catch (APIConnectionException e) {
            throw new TelnyxException("Connection error: " + e.getMessage(), e);
        }
    }
}

// src/main/java/com/telnyx/controller/LocationController.java
package com.telnyx.controller;

import com.telnyx.model.DeviceLocation;
import com.telnyx.service.LocationService;
import com.telnyx.exception.TelnyxException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/devices")
public class LocationController {

    private final LocationService locationService;

    @Autowired
    public LocationController(LocationService locationService) {
        this.locationService = locationService;
    }

    @GetMapping("/locations")
    public ResponseEntity<?> getAllLocations() {
        try {
            List<DeviceLocation> locations = locationService.getAllDeviceLocations();
            return ResponseEntity.ok(locations);
        } catch (TelnyxException e) {
            return handleTelnyxException(e);
        }
    }

    @GetMapping("/{simCardId}/location")
    public ResponseEntity<?> getLocationBySim(@PathVariable String simCardId) {
        if (simCardId == null || simCardId.trim().isEmpty()) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "SIM card ID is required");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            DeviceLocation location = locationService.getDeviceLocationBySim(simCardId);
            return ResponseEntity.ok(location);
        } catch (TelnyxException e) {
            return handleTelnyxException(e);
        }
    }

    private ResponseEntity<?> handleTelnyxException(TelnyxException e) {
        Map<String, String> error = new HashMap<>();
        error.put("error", e.getMessage());

        String message = e.getMessage();
        if (message != null && message.contains("Authentication failed")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
        } else if (message != null && message.contains("Rate limit exceeded")) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
        } else if (message != null && message.contains("Connection error")) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
        } else {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }
}
