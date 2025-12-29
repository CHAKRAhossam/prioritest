package com.testprioritization.controller;

import com.testprioritization.config.AppProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.reactive.server.WebTestClient;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@WebFluxTest(HealthController.class)
class HealthControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private AppProperties appProperties;

    @MockBean(name = "trainingWebClient")
    private WebClient trainingWebClient;

    @MockBean(name = "prioritizationWebClient")
    private WebClient prioritizationWebClient;

    @MockBean
    private AppProperties.PolicyGate policyGate;

    @MockBean
    private AppProperties.Training training;

    @MockBean
    private AppProperties.Risk risk;

    @MockBean
    private AppProperties.Risk.Threshold threshold;

    @BeforeEach
    void setUp() {
        when(appProperties.getPolicyGate()).thenReturn(policyGate);
        when(appProperties.getTraining()).thenReturn(training);
        when(appProperties.getRisk()).thenReturn(risk);
        when(risk.getThreshold()).thenReturn(threshold);
        when(policyGate.isEnabled()).thenReturn(true);
        when(policyGate.isBlockOnHighRisk()).thenReturn(false);
        when(training.isEnabled()).thenReturn(true);
        when(threshold.getHigh()).thenReturn(0.7);
        when(threshold.getMedium()).thenReturn(0.3);
    }

    @Test
    void testLiveness() {
        webTestClient.get()
                .uri("/v1/health/live")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").isEqualTo("UP")
                .jsonPath("$.timestamp").exists();
    }

    @Test
    void testReadiness() {
        // Mock WebClient responses
        WebClient.RequestHeadersUriSpec requestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        WebClient.RequestHeadersSpec requestHeadersSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersSpec.class);
        WebClient.ResponseSpec responseSpec = org.mockito.Mockito.mock(WebClient.ResponseSpec.class);

        when(trainingWebClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(any(String.class))).thenReturn(requestHeadersSpec);
        when(requestHeadersSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        when(prioritizationWebClient.get()).thenReturn(requestHeadersUriSpec);
        when(prioritizationWebClient.get().uri(any(String.class))).thenReturn(requestHeadersSpec);

        webTestClient.get()
                .uri("/v1/health/ready")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").exists();
    }

    @Test
    void testHealth() {
        // Mock WebClient responses
        WebClient.RequestHeadersUriSpec requestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        WebClient.RequestHeadersSpec requestHeadersSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersSpec.class);
        WebClient.ResponseSpec responseSpec = org.mockito.Mockito.mock(WebClient.ResponseSpec.class);

        when(trainingWebClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(any(String.class))).thenReturn(requestHeadersSpec);
        when(requestHeadersSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        when(prioritizationWebClient.get()).thenReturn(requestHeadersUriSpec);
        when(prioritizationWebClient.get().uri(any(String.class))).thenReturn(requestHeadersSpec);

        webTestClient.get()
                .uri("/v1/health")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.application").exists()
                .jsonPath("$.status").isEqualTo("UP");
    }
}

