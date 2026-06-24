package com.telnyx.iot;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class ESimProvisioningApplication {
    public static void main(String[] args) {
        SpringApplication.run(ESimProvisioningApplication.class, args);
    }
}

@Configuration
class TelnyxConfig {
    @Value("${telnyx.api-key}")
    private String apiKey;

    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.builder()
                .apiKey(apiKey)
                .build();
    }
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class ESimProvisioningRequest {
    private String iccid;
    private String deviceName;
    private String apn;
    private String simCardGroupId;
    private String activationCode;
}

@Slf4j
@Service
@RequiredArgsConstructor
class ESimProvisioningService {
    private final TelnyxClient telnyxClient;

    public Map<String, Object> provisionESim(ESimProvisioningRequest request) {
        log.info("Starting eSIM provisioning for ICCID: {}", request.getIccid());

        if (request.getIccid() == null || request.getIccid().isEmpty()) {
            throw new IllegalArgumentException("ICCID is required");
        }

        if (request.getApn() == null || request.getApn().isEmpty()) {
            request.setApn("internet.telnyx");
        }

        try {
            var simCard = telnyxClient.simCards().retrieve(request.getIccid());
            log.info("Retrieved SIM card: {}", simCard.getData().getId());

            if (!"active".equals(simCard.getData().getStatus())) {
                var activateResponse = telnyxClient.simCards().activate(
                        simCard.getData().getId(),
                        new HashMap<>()
                );
                log.info("SIM card activated: {}", activateResponse.getData().getId());
            }

            return Map.of(
                    "simCardId", simCard.getData().getId(),
                    "iccid", simCard.getData().getIccid(),
                    "status", simCard.getData().getStatus(),
                    "apn", request.getApn(),
                    "deviceName", request.getDeviceName(),
                    "provisioningStatus", "success",
                    "message", "eSIM profile provisioned successfully"
            );

        } catch (AuthenticationException e) {
            log.error("Authentication failed: {}", e.getMessage());
            throw new RuntimeException("Invalid API key", e);
        } catch (RateLimitException e) {
            log.error("Rate limit exceeded: {}", e.getMessage());
            throw new RuntimeException("Rate limit exceeded. Please retry after a delay.", e);
        } catch (TelnyxException e) {
            log.error("Telnyx API error: {}", e.getMessage());
            throw new RuntimeException("Failed to provision eSIM: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> getESIMStatus(String simCardId) {
        try {
            var simCard = telnyxClient.simCards().retrieve(simCardId);
            var data = simCard.getData();

            return Map.of(
                    "simCardId", data.getId(),
                    "iccid", data.getIccid(),
                    "status", data.getStatus(),
                    "simCardGroupId", data.getSimCardGroupId() != null ? data.getSimCardGroupId() : "N/A",
                    "createdAt", data.getCreatedAt() != null ? data.getCreatedAt().toString() : "N/A"
            );

        } catch (TelnyxException e) {
            log.error("Failed to retrieve eSIM status: {}", e.getMessage());
            throw new RuntimeException("Failed to retrieve eSIM status: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> listSimCardsInGroup(String simCardGroupId) {
        try {
            var response = telnyxClient.simCards().list(
                    Map.of("filter[sim_card_group_id]", simCardGroupId)
            );

            var simCards = response.getData().stream()
                    .map(sim -> Map.of(
                            "id", sim.getId(),
                            "iccid", sim.getIccid(),
                            "status", sim.getStatus()
                    ))
                    .toList();

            return Map.of(
                    "simCardGroupId", simCardGroupId,
                    "totalCount", simCards.size(),
                    "simCards", simCards
            );

        } catch (TelnyxException e) {
            log.error("Failed to list SIM cards: {}", e.getMessage());
            throw new RuntimeException("Failed to list SIM cards: " + e.getMessage(), e);
        }
    }
}

@Slf4j
@RestController
@RequestMapping("/esim")
@RequiredArgsConstructor
class ESimProvisioningController {
    private final ESimProvisioningService eSimProvisioningService;

    @PostMapping("/provision")
    public ResponseEntity<Map<String, Object>> provisionESim(
            @RequestBody ESimProvisioningRequest request) {
        log.info("Received eSIM provisioning request for ICCID: {}", request.getIccid());

        try {
            var result = eSimProvisioningService.provisionESim(request);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/{simCardId}/status")
    public ResponseEntity<Map<String, Object>> getESIMStatus(
            @PathVariable String simCardId) {
        log.info("Retrieving eSIM status for SIM card ID: {}", simCardId);

        try {
            var result = eSimProvisioningService.getESIMStatus(simCardId);
            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/group/{simCardGroupId}/list")
    public ResponseEntity<Map<String, Object>> listSimCardsInGroup(
            @PathVariable String simCardGroupId) {
        log.info("Listing SIM cards in group: {}", simCardGroupId);

        try {
            var result = eSimProvisioningService.listSimCardsInGroup(simCardGroupId);
            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}

@Slf4j
@RestController
@RequestMapping("/webhooks")
@RequiredArgsConstructor
class WebhookController {
    @PostMapping("/sim-events")
    public ResponseEntity<Map<String, String>> handleSimEvent(
            @RequestBody Map<String, Object> payload) {
        log.info("Received webhook event: {}", payload);

        try {
            String eventType = (String) payload.get("type");
            Map<String, Object> data = (Map<String, Object>) payload.get("data");

            if ("sim_card.status.changed".equals(eventType)) {
                String simCardId = (String) data.get("id");
                String newStatus = (String) data.get("status");
                log.info("SIM card {} status changed to: {}", simCardId, newStatus);
            } else if ("sim_card.data_limit.reached".equals(eventType)) {
                String simCardId = (String) data.get("id");
                log.warn("SIM card {} has reached its data limit", simCardId);
            } else if ("sim_card.network.attached".equals(eventType)) {
                String simCardId = (String) data.get("id");
                log.info("SIM card {} attached to network", simCardId);
            }

            return ResponseEntity.ok(Map.of("status", "received"));

        } catch (Exception e) {
            log.error("Error processing webhook: {}", e.getMessage());
            return ResponseEntity.status(500)
                    .body(Map.of("error", "Failed to process webhook"));
        }
    }
}
