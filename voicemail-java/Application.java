package com.telnyx.voicemail;

import com.telnyx.sdk.TelnyxClient;
import com.telnyx.sdk.TelnyxOkHttpClient;
import com.telnyx.sdk.exception.ApiException;
import com.telnyx.sdk.model.CallControlCommandResponse;
import com.telnyx.sdk.model.CallInitiateRequest;
import com.telnyx.sdk.model.CallRecordingStartRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@SpringBootApplication
public class VoicemailApplication {

    public static void main(String[] args) {
        SpringApplication.run(VoicemailApplication.class, args);
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
class VoicemailService {

    @Autowired
    private TelnyxClient telnyxClient;

    @Value("${telnyx.phone.number}")
    private String fromNumber;

    @Value("${telnyx.connection.id}")
    private String connectionId;

    public Map<String, Object> initiateVoicemailCall(String toNumber) throws ApiException {
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
        }

        CallInitiateRequest request = new CallInitiateRequest();
        request.setFrom(fromNumber);
        request.setTo(toNumber);
        request.setConnectionId(connectionId);

        CallControlCommandResponse response = telnyxClient.calls().dial(request);

        return Map.of(
            "call_control_id", response.getData().getCallControlId(),
            "call_state", response.getData().getCallState(),
            "from", fromNumber,
            "to", toNumber
        );
    }

    public Map<String, Object> startVoicemailRecording(String callControlId) throws ApiException {
        CallRecordingStartRequest request = new CallRecordingStartRequest();
        request.setFormat("wav");
        request.setChannels("single");

        CallControlCommandResponse response = telnyxClient.calls().actions().startRecording(callControlId, request);

        return Map.of(
            "call_control_id", response.getData().getCallControlId(),
            "recording_state", "started"
        );
    }

    public Map<String, Object> stopVoicemailRecording(String callControlId) throws ApiException {
        CallControlCommandResponse response = telnyxClient.calls().actions().stopRecording(callControlId);

        return Map.of(
            "call_control_id", response.getData().getCallControlId(),
            "recording_state", "stopped"
        );
    }

    public Map<String, Object> hangupCall(String callControlId) throws ApiException {
        CallControlCommandResponse response = telnyxClient.calls().actions().hangup(callControlId);

        return Map.of(
            "call_control_id", response.getData().getCallControlId(),
            "call_state", response.getData().getCallState()
        );
    }
}

@RestController
@RequestMapping("/api/voicemail")
class VoicemailController {

    @Autowired
    private VoicemailService voicemailService;

    @PostMapping("/initiate")
    public ResponseEntity<?> initiateVoicemail(@RequestBody Map<String, String> request) {
        String toNumber = request.get("to");

        if (toNumber == null || toNumber.isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Missing required field: 'to'"));
        }

        try {
            Map<String, Object> result = voicemailService.initiateVoicemailCall(toNumber);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", e.getMessage()));
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/{callControlId}/start-recording")
    public ResponseEntity<?> startRecording(@PathVariable String callControlId) {
        try {
            Map<String, Object> result = voicemailService.startVoicemailRecording(callControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/{callControlId}/stop-recording")
    public ResponseEntity<?> stopRecording(@PathVariable String callControlId) {
        try {
            Map<String, Object> result = voicemailService.stopVoicemailRecording(callControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/{callControlId}/hangup")
    public ResponseEntity<?> hangup(@PathVariable String callControlId) {
        try {
            Map<String, Object> result = voicemailService.hangupCall(callControlId);
            return ResponseEntity.ok(result);
        } catch (ApiException e) {
            return handleApiException(e);
        }
    }

    @PostMapping("/webhooks/voice")
    public ResponseEntity<?> handleVoiceWebhook(@RequestBody Map<String, Object> payload) {
        String eventType = (String) payload.get("event_type");
        Map<String, Object> data = (Map<String, Object>) payload.get("data");

        switch (eventType) {
            case "call.initiated":
                System.out.println("Call initiated: " + data.get("call_control_id"));
                break;
            case "call.answered":
                System.out.println("Call answered: " + data.get("call_control_id"));
                break;
            case "call.hangup":
                System.out.println("Call hung up: " + data.get("call_control_id"));
                break;
            case "call.recording.saved":
                System.out.println("Recording saved: " + data.get("recording_url"));
                break;
            default:
                System.out.println("Unhandled event type: " + eventType);
        }

        return ResponseEntity.ok(Map.of("status", "received"));
    }

    private ResponseEntity<?> handleApiException(ApiException e) {
        int statusCode = e.getCode();

        if (statusCode == 401) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid API key"));
        } else if (statusCode == 429) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } else if (statusCode >= 400 && statusCode < 500) {
            return ResponseEntity.status(statusCode)
                .body(Map.of("error", e.getMessage(), "status_code", statusCode));
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "Network error connecting to Telnyx"));
        }
    }
}
