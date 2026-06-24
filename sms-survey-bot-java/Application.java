// pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.telnyx</groupId>
    <artifactId>sms-survey</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
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
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
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

// src/main/java/com/telnyx/Application.java
package com.telnyx;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
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

// src/main/java/com/telnyx/model/Survey.java
package com.telnyx.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;

@Entity
@Table(name = "surveys")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Survey {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String phoneNumber;
    private String currentQuestion;
    private Integer questionIndex;
    private String responses;
    private String status;

    public Survey(String phoneNumber) {
        this.phoneNumber = phoneNumber;
        this.questionIndex = 0;
        this.responses = "";
        this.status = "pending";
    }
}

// src/main/java/com/telnyx/repository/SurveyRepository.java
package com.telnyx.repository;

import com.telnyx.model.Survey;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SurveyRepository extends JpaRepository<Survey, Long> {
    Optional<Survey> findByPhoneNumber(String phoneNumber);
}

// src/main/java/com/telnyx/service/SurveyService.java
package com.telnyx.service;

import com.telnyx.model.Survey;
import com.telnyx.repository.SurveyRepository;
import com.telnyx.sdk.TelnyxClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

@Service
public class SurveyService {

    private static final List<String> SURVEY_QUESTIONS = Arrays.asList(
        "How satisfied are you with our service? Reply 1-5.",
        "Would you recommend us to a friend? Reply YES or NO.",
        "What could we improve? Reply with your feedback."
    );

    @Autowired
    private TelnyxClient telnyxClient;

    @Autowired
    private SurveyRepository surveyRepository;

    @Value("${TELNYX_PHONE_NUMBER:+15551234567}")
    private String fromNumber;

    public void startSurvey(String toNumber) throws Exception {
        if (!toNumber.startsWith("+")) {
            throw new IllegalArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");
        }

        Optional<Survey> existing = surveyRepository.findByPhoneNumber(toNumber);
        if (existing.isPresent()) {
            throw new IllegalStateException("Survey already in progress for this number");
        }

        Survey survey = new Survey(toNumber);
        survey.setCurrentQuestion(SURVEY_QUESTIONS.get(0));
        survey.setQuestionIndex(0);
        survey.setStatus("in_progress");
        surveyRepository.save(survey);

        sendSurveyQuestion(toNumber, SURVEY_QUESTIONS.get(0));
    }

    public void processResponse(String fromNumber, String responseText) throws Exception {
        Optional<Survey> surveyOpt = surveyRepository.findByPhoneNumber(fromNumber);
        if (!surveyOpt.isPresent()) {
            return;
        }

        Survey survey = surveyOpt.get();

        if (!survey.getResponses().isEmpty()) {
            survey.setResponses(survey.getResponses() + " | ");
        }
        survey.setResponses(survey.getResponses() + responseText);

        int nextIndex = survey.getQuestionIndex() + 1;
        if (nextIndex < SURVEY_QUESTIONS.size()) {
            survey.setQuestionIndex(nextIndex);
            survey.setCurrentQuestion(SURVEY_QUESTIONS.get(nextIndex));
            surveyRepository.save(survey);
            sendSurveyQuestion(fromNumber, SURVEY_QUESTIONS.get(nextIndex));
        } else {
            survey.setStatus("completed");
            surveyRepository.save(survey);
            sendSurveyQuestion(fromNumber, "Thank you for completing the survey!");
        }
    }

    private void sendSurveyQuestion(String toNumber, String questionText) throws Exception {
        telnyxClient.messages().create(
            com.telnyx.sdk.model.MessageCreateRequest.builder()
                .from(fromNumber)
                .to(toNumber)
                .text(questionText)
                .build()
        );
    }

    public Optional<Survey> getSurveyResults(String phoneNumber) {
        return surveyRepository.findByPhoneNumber(phoneNumber);
    }
}

// src/main/java/com/telnyx/controller/SurveyController.java
package com.telnyx.controller;

import com.telnyx.model.Survey;
import com.telnyx.service.SurveyService;
import com.telnyx.sdk.exception.ApiException;
import com.telnyx.sdk.exception.AuthenticationException;
import com.telnyx.sdk.exception.RateLimitException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/survey")
public class SurveyController {

    @Autowired
    private SurveyService surveyService;

    @PostMapping("/start")
    public ResponseEntity<?> startSurvey(@RequestBody Map<String, String> request) {
        String toNumber = request.get("phone_number");

        if (toNumber == null || toNumber.isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Missing required field: 'phone_number'"));
        }

        try {
            surveyService.startSurvey(toNumber);
            return ResponseEntity.ok(Map.of(
                "message", "Survey started",
                "phone_number", toNumber
            ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("error", e.getMessage()));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid API key"));
        } catch (RateLimitException e) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .body(Map.of("error", "Rate limit exceeded. Please slow down."));
        } catch (ApiException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(Map.of("error", "Telnyx API error: " + e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Unexpected error: " + e.getMessage()));
        }
    }

    @PostMapping("/webhooks/sms")
    public ResponseEntity<?> handleInboundSms(@RequestBody Map<String, Object> payload) {
        try {
            String eventType = (String) payload.get("type");
            if (!"message.received".equals(eventType)) {
                return ResponseEntity.ok(Map.of("status", "ignored"));
            }

            Map<String, Object> data = (Map<String, Object>) payload.get("data");
            if (data == null) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing data field"));
            }

            String fromNumber = (String) data.get("from");
            String messageText = (String) data.get("text");

            if (fromNumber == null || messageText == null) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Missing from or text field"));
            }

            surveyService.processResponse(fromNumber, messageText);

            return ResponseEntity.ok(Map.of("status", "processed"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Webhook processing error: " + e.getMessage()));
        }
    }

    @GetMapping("/results/{phoneNumber}")
    public ResponseEntity<?> getSurveyResults(@PathVariable String phoneNumber) {
        Optional<Survey> survey = surveyService.getSurveyResults(phoneNumber);

        if (!survey.isPresent()) {
            return ResponseEntity.notFound().build();
        }

        Survey s = survey.get();
        return ResponseEntity.ok(Map.of(
            "id", s.getId(),
            "phone_number", s.getPhoneNumber(),
            "status", s.getStatus(),
            "responses", s.getResponses(),
            "current_question", s.getCurrentQuestion()
        ));
    }
}

// src/main/resources/application.properties
spring.application.name=sms-survey
server.port=8080
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.h2.console.enabled=true
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
