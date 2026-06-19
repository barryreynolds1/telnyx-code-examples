package com.telnyx.sms;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.TelnyxException;
import com.telnyx.sdk.TelnyxOkHttpClient;
import com.telnyx.sdk.model.MessageRequest;
import com.telnyx.sdk.model.MessageResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class SmsApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmsApplication.class, args);
    }
}

@RestController
@RequestMapping("/sms")
class SmsController {
    private final SmsService smsService;

    public SmsController(SmsService smsService) {
        this.smsService = smsService;
    }

    @PostMapping("/send")
    public ResponseEntity<Map<String, Object>> sendSms(@RequestBody SmsRequest request) {
        if (request.getTo() == null || request.getMessage() == null) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Missing required fields: 'to' and 'message'");
            return ResponseEntity.badRequest().body(error);
        }

        try {
            Map<String, Object> result = smsService.sendSms(request.getTo(), request.getMessage());
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        } catch (TelnyxException e) {
            // Catch Telnyx exceptions ONLY in the route handler
            Map<String, Object> error = new HashMap<>();
            int statusCode = e.getStatusCode();
            
            if (statusCode == 401) {
                error.put("error", "Invalid API key");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            } else if (statusCode == 429) {
                error.put("error", "Rate limit exceeded. Please slow down.");
                return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
            } else {
                error.put("error", e.getMessage());
                error.put("status_code", statusCode);
                return ResponseEntity.status(statusCode).body(error);
            }
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Network error connecting to Telnyx");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
        }
    }
}

@Service
class SmsService {
    private final TelnyxClient client;
    private final String fromNumber;

    public SmsService(@Value("${TELNYX_PHONE_NUMBER}") String fromNumber) {
        if (fromNumber == null || fromNumber.isEmpty()) {
            throw new IllegalStateException("TELNYX_PHONE_NUMBER environment variable not set");
        }
        this.fromNumber = fromNumber;
        // Initialize client using new pattern — reads TELNYX_API_KEY from environment
        this.client = TelnyxOkHttpClient.fromEnv();
    }

    public Map<String, Object> sendSms(String toNumber, String message) {
        // Validate E.164 format to prevent API errors
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
        }

        MessageRequest msgRequest = MessageRequest.builder()
                .from(fromNumber)
                .to(toNumber)
                .text(message)
                .build();

        // Use client.messages().create() — NOT static client.messages.create()
        MessageResponse response = client.messages().create(msgRequest);

        // Extract serializable data — do not return raw response object
        Map<String, Object> result = new HashMap<>();
        result.put("message_id", response.getData().getId());
        if (response.getData().getTo() != null && !response.getData().getTo().isEmpty()) {
            result.put("status", response.getData().getTo().get(0).getStatus());
        } else {
            result.put("status", "unknown");
        }
        result.put("from", fromNumber);
        result.put("to", toNumber);
        
        return result;
    }
}

class SmsRequest {
    private String to;
    private String message;

    public String getTo() { return to; }
    public void setTo(String to) { this.to = to; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
