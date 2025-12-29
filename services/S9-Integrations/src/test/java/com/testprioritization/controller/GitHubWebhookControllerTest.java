package com.testprioritization.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.testprioritization.config.AppProperties;
import com.testprioritization.model.webhook.GitHubWebhook;
import com.testprioritization.service.CommentGeneratorService;
import com.testprioritization.service.GitHubService;
import com.testprioritization.service.PolicyGateService;
import com.testprioritization.service.RiskAnalyzerService;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Tracer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@WebFluxTest(GitHubWebhookController.class)
class GitHubWebhookControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private GitHubService gitHubService;

    @MockBean
    private RiskAnalyzerService riskAnalyzerService;

    @MockBean
    private PolicyGateService policyGateService;

    @MockBean
    private CommentGeneratorService commentGeneratorService;

    @MockBean
    private AppProperties appProperties;

    @MockBean
    private ObjectMapper objectMapper;

    @MockBean
    private Tracer tracer;

    @MockBean
    private MeterRegistry meterRegistry;

    private String webhookPayload;

    @BeforeEach
    void setUp() {
        webhookPayload = """
            {
                "action": "opened",
                "pull_request": {
                    "number": 123,
                    "head": {
                        "sha": "abc123",
                        "ref": "feature-branch"
                    }
                },
                "repository": {
                    "full_name": "test/repo"
                }
            }
            """;
    }

    @Test
    void testHandleWebhook() {
        webTestClient.post()
                .uri("/v1/webhooks/github")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(webhookPayload)
                .exchange()
                .expectStatus().isOk();
    }

    @Test
    void testHandleWebhookWithInvalidSignature() {
        webTestClient.post()
                .uri("/v1/webhooks/github")
                .header("X-Hub-Signature-256", "invalid")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(webhookPayload)
                .exchange()
                .expectStatus().is4xxClientError();
    }
}

