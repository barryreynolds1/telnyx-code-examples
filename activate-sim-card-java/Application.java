package com.telnyx;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import com.telnyx.exception.AuthenticationException;
import com.telnyx.exception.RateLimitException;
import com.telnyx.exception.TelnyxException;
import com.telnyx.model.SimCard;
import com.telnyx.model.SimCardActivateResponse;

import java.util.Map;

@SpringBootApplication
public class SimActivationApplication {

    public static void main(String[] args) {
        Dotenv dotenv = Dotenv.load();
        SpringApplication.run(SimActivationApplication.class, args);
    }
}

@Configuration
class TelnyxConfig {
    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}

@Service
class SimCardService {
    private final TelnyxClient telnyxClient;

    public SimCardService(TelnyxClient telnyxClient) {
        this.telnyxClient = telnyxClient;
    }

    public Map<String, Object> getSimCard(String simCardId) throws TelnyxException {
        SimCard simCard = telnyxClient.simCards().retrieve(simCardId);
        return Map.of(
            "id", simCard.getId(),
            "iccid", simCard.getIccid() != null ? simCard.getIccid() : "N/A",
            "status", simCard.getStatus() != null ? simCard.getStatus() : "unknown",
            "simCardGroupId", simCard.getSimCardGroupId() != null ? simCard.getSimCardGroupId() : "N/A"
        );
    }

    public Map<String, Object> activateSimCard(String simCardId) throws TelnyxException {
        if (simCardId == null || simCardId.trim().isEmpty()) {
            throw new IllegalArgumentException("SIM card ID cannot be empty");
        }

        SimCardActivateResponse response = telnyxClient.simCards().activate(simCardId);
        SimCard activatedSim = response.getData();

        return Map.of(
            "id", activatedSim.getId(),
            "iccid", activatedSim.getIccid() != null ? activatedSim.getIccid() : "N/A",
            "status", activatedSim.getStatus() != null ? activatedSim.getStatus() : "unknown",
            "simCardGroupId", activatedSim.getSimCardGroupId() != null ? activatedSim.getSimCardGroupId() : "N/A",
            "message", "SIM card activated successfully"
        );
    }
}

@RestController
@RequestMapping("/api/sim-cards")
class SimCardController {
    private final SimCardService simCardService;

    public SimCardController(SimCardService simCardService) {
        this.simCardService = simCardService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getSimCard(@PathVariable String id) {
        try {
            Map<String, Object> simCard = simCardService.getSimCard(id);
            return ResponseEntity.ok(simCard);
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

    @PostMapping("/{id}/activate")
    public ResponseEntity<Map<String, Object>> activateSimCard(@PathVariable String id) {
        try {
            Map<String, Object> result = simCardService.activateSimCard(id);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
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
}
