package com.telnyx;

import com.telnyx.TelnyxClient;
import com.telnyx.TelnyxOkHttpClient;
import com.telnyx.exception.TelnyxException;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@SpringBootApplication
public class ScheduledSmsApplication {
    public static void main(String[] args) {
        SpringApplication.run(ScheduledSmsApplication.class, args);
    }
}

@Configuration
@EnableScheduling
class TelnyxConfig {
    @Bean
    public TelnyxClient telnyxClient() {
        return TelnyxOkHttpClient.fromEnv();
    }
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class ScheduledSmsRequest {
    private String to;
    private String message;
    private LocalDateTime scheduledTime;
}

@Service
@Slf4j
class SmsSchedulerService {
    @Autowired
    private TelnyxClient telnyxClient;

    @Value("${telnyx.phone.number}")
    private String fromNumber;

    private final Map<String, ScheduledSmsRequest> scheduledMessages = new ConcurrentHashMap<>();

    public Map<String, Object> scheduleMessage(ScheduledSmsRequest request) {
        if (!request.getTo().startsWith("+")) {
            throw new IllegalArgumentException(
                "Phone number must be in E.164 format (e.g., +15551234567)"
            );
        }

        if (request.getScheduledTime().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException(
                "Scheduled time must be in the future"
            );
        }

        String messageId = "sched_" + System.currentTimeMillis();
        scheduledMessages.put(messageId, request);

        log.info("Message {} scheduled for {}", messageId, request.getScheduledTime());

        return Map.of(
            "message_id", messageId,
            "status", "scheduled",
            "scheduled_time", request.getScheduledTime().toString(),
            "to", request.getTo()
        );
    }

    @Scheduled(fixedRate = 60000)
    public void processPendingMessages() {
        LocalDateTime now = LocalDateTime.now();
        List<String> messagesToRemove = new ArrayList<>();

        for (Map.Entry<String, ScheduledSmsRequest> entry : scheduledMessages.entrySet()) {
            String messageId = entry.getKey();
            ScheduledSmsRequest request = entry.getValue();

            if (now.isAfter(request.getScheduledTime()) || now.equals(request.getScheduledTime())) {
                try {
                    sendSms(messageId, request);
                    messagesToRemove.add(messageId);
                } catch (Exception e) {
                    log.error("Failed to send scheduled message {}: {}", messageId, e.getMessage());
                }
            }
        }

        messagesToRemove.forEach(scheduledMessages::remove);
    }

    private void sendSms(String messageId, ScheduledSmsRequest request) {
        try {
            var response = telnyxClient.messages().create(
                Map.of(
                    "from_", fromNumber,
                    "to", request.getTo(),
                    "text", request.getMessage()
                )
            );

            log.info(
                "Message {} sent successfully. Telnyx ID: {}",
                messageId,
                response.getData().getId()
            );
        } catch (TelnyxException e) {
            log.error("Telnyx API error sending message {}: {}", messageId, e.getMessage());
            throw new RuntimeException("Failed to send SMS: " + e.getMessage(), e);
        }
    }

    public List<Map<String, Object>> getScheduledMessages() {
        return scheduledMessages.entrySet().stream()
            .map(entry -> Map.of(
                "message_id", entry.getKey(),
                "to", entry.getValue().getTo(),
                "scheduled_time", entry.getValue().getScheduledTime().toString(),
                "message", entry.getValue().getMessage()
            ))
            .toList();
    }
}

@RestController
@RequestMapping("/api/sms")
@Slf4j
class SmsController {
    @Autowired
    private SmsSchedulerService smsSchedulerService;

    @PostMapping("/schedule")
    public ResponseEntity<Map<String, Object>> scheduleSms(@RequestBody ScheduledSmsRequest request) {
        try {
            Map<String, Object> result = smsSchedulerService.scheduleMessage(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(result);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/scheduled")
    public ResponseEntity<List<Map<String, Object>>> getScheduledMessages() {
        List<Map<String, Object>> messages = smsSchedulerService.getScheduledMessages();
        return ResponseEntity.ok(messages);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleException(Exception e) {
        log.error("Unexpected error: {}", e.getMessage(), e);

        if (e.getMessage() != null && e.getMessage().contains("401")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid API key"));
        } else if (e.getMessage() != null && e.getMessage().contains("429")) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } else if (e.getMessage() != null && e.getMessage().contains("503")) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "Network error connecting to Telnyx"));
        }

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(Map.of("error", "Internal server error: " + e.getMessage()));
    }
}
