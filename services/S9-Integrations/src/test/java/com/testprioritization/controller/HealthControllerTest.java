package com.testprioritization.controller;

import com.testprioritization.config.AppProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.reactive.server.WebTestClient;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
@ActiveProfiles("test")
class HealthControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private AppProperties appProperties;

    @MockBean
    private WebClient trainingWebClient;

    @MockBean
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
        // Mock WebClient responses using doReturn to avoid type issues
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersUriSpec<?> trainingRequestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersUriSpec<?> prioritizationRequestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersSpec<?> requestHeadersSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersSpec.class);
        WebClient.ResponseSpec responseSpec = org.mockito.Mockito.mock(WebClient.ResponseSpec.class);

        org.mockito.Mockito.doReturn(trainingRequestHeadersUriSpec).when(trainingWebClient).get();
        org.mockito.Mockito.doReturn(requestHeadersSpec).when(trainingRequestHeadersUriSpec).uri(any(String.class));
        org.mockito.Mockito.doReturn(responseSpec).when(requestHeadersSpec).retrieve();
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        org.mockito.Mockito.doReturn(prioritizationRequestHeadersUriSpec).when(prioritizationWebClient).get();
        org.mockito.Mockito.doReturn(requestHeadersSpec).when(prioritizationRequestHeadersUriSpec).uri(any(String.class));
        org.mockito.Mockito.doReturn(responseSpec).when(requestHeadersSpec).retrieve();
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        webTestClient.get()
                .uri("/v1/health/ready")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").exists();
    }

    @Test
    void testHealth() {
        // Mock WebClient responses using doReturn to avoid type issues
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersUriSpec<?> trainingRequestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersUriSpec<?> prioritizationRequestHeadersUriSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersUriSpec.class);
        @SuppressWarnings("unchecked")
        WebClient.RequestHeadersSpec<?> requestHeadersSpec = org.mockito.Mockito.mock(WebClient.RequestHeadersSpec.class);
        WebClient.ResponseSpec responseSpec = org.mockito.Mockito.mock(WebClient.ResponseSpec.class);

        org.mockito.Mockito.doReturn(trainingRequestHeadersUriSpec).when(trainingWebClient).get();
        org.mockito.Mockito.doReturn(requestHeadersSpec).when(trainingRequestHeadersUriSpec).uri(any(String.class));
        org.mockito.Mockito.doReturn(responseSpec).when(requestHeadersSpec).retrieve();
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        org.mockito.Mockito.doReturn(prioritizationRequestHeadersUriSpec).when(prioritizationWebClient).get();
        org.mockito.Mockito.doReturn(requestHeadersSpec).when(prioritizationRequestHeadersUriSpec).uri(any(String.class));
        org.mockito.Mockito.doReturn(responseSpec).when(requestHeadersSpec).retrieve();
        when(responseSpec.bodyToMono(Map.class)).thenReturn(Mono.just(Map.of("status", "UP")));

        webTestClient.get()
                .uri("/v1/health")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.application").exists()
                .jsonPath("$.status").isEqualTo("UP");
    }
}

