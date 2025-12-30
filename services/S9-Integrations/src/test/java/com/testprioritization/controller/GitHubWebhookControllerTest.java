package com.testprioritization.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.testprioritization.config.AppProperties;
import com.testprioritization.service.CommentGeneratorService;
import com.testprioritization.service.GitHubService;
import com.testprioritization.service.PolicyGateService;
import com.testprioritization.service.RiskAnalyzerService;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Tracer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.reactive.server.WebTestClient;

import reactor.core.publisher.Mono;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
@ActiveProfiles("test")
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
                    "full_name": "test/repo",
                    "name": "repo",
                    "owner": {
                        "login": "test"
                    }
                }
            }
            """;
        
        // Mock AppProperties to avoid signature validation
        when(appProperties.getGithub()).thenReturn(new AppProperties.GitHub());
        when(appProperties.getGithub().getWebhookSecret()).thenReturn(null);
        
        // Mock services to return empty results
        when(gitHubService.createCheckRun(any(), any(), any(), any(), any()))
            .thenReturn(Mono.just(Map.of("id", 123L)));
        when(gitHubService.getPRFiles(any(), any(), any(), any()))
            .thenReturn(Mono.just(java.util.Collections.emptyList()));
        when(riskAnalyzerService.analyzeRisk(any(), any(), any(), any()))
            .thenReturn(Mono.just(new com.testprioritization.model.response.RiskAnalysisResult()));
        when(policyGateService.evaluatePolicy(any()))
            .thenReturn(com.testprioritization.service.PolicyGateService.PolicyGateResult.builder()
                .passed(true)
                .shouldBlock(false)
                .violations(java.util.Collections.emptyList())
                .build());
        when(commentGeneratorService.generateComment(any(), any()))
            .thenReturn(new com.testprioritization.model.response.PRComment());
        when(gitHubService.updateCheckRun(any(), any(), any(), any(), any()))
            .thenReturn(Mono.just(Map.of()));
        when(gitHubService.postPRComment(any(), any(), any(), any(), any()))
            .thenReturn(Mono.just(Map.of()));
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

