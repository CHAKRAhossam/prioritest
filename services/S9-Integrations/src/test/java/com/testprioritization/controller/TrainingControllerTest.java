package com.testprioritization.controller;

import com.testprioritization.service.TrainingTriggerService;
import com.testprioritization.service.TrainingTriggerService.TrainingRequest;
import com.testprioritization.service.TrainingTriggerService.TrainingResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;
import reactor.core.publisher.Mono;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@WebFluxTest(TrainingController.class)
class TrainingControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private TrainingTriggerService trainingTriggerService;

    private TrainingResponse successResponse;
    private TrainingResponse failedResponse;

    @BeforeEach
    void setUp() {
        successResponse = new TrainingResponse();
        successResponse.setStatus("SUCCESS");
        successResponse.setJobId("job-123");
        successResponse.setMessage("Training started");

        failedResponse = new TrainingResponse();
        failedResponse.setStatus("FAILED");
        failedResponse.setJobId("job-456");
        failedResponse.setMessage("Training failed");
    }

    @Test
    void testTriggerTraining() {
        TrainingRequest request = new TrainingRequest();
        request.setTriggerType("MANUAL");

        when(trainingTriggerService.triggerTraining(any(TrainingRequest.class)))
                .thenReturn(Mono.just(successResponse));

        webTestClient.post()
                .uri("/v1/training/trigger")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue("{\"triggerType\":\"MANUAL\"}")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").isEqualTo("SUCCESS");
    }

    @Test
    void testTriggerTrainingFailed() {
        TrainingRequest request = new TrainingRequest();
        request.setTriggerType("MANUAL");

        when(trainingTriggerService.triggerTraining(any(TrainingRequest.class)))
                .thenReturn(Mono.just(failedResponse));

        webTestClient.post()
                .uri("/v1/training/trigger")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue("{\"triggerType\":\"MANUAL\"}")
                .exchange()
                .expectStatus().isBadRequest();
    }

    @Test
    void testGetTrainingStatus() {
        when(trainingTriggerService.getTrainingStatus(anyString()))
                .thenReturn(Mono.just(successResponse));

        webTestClient.get()
                .uri("/v1/training/status/job-123")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").isEqualTo("SUCCESS")
                .jsonPath("$.jobId").isEqualTo("job-123");
    }
}

