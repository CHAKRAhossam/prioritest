package com.prioritest.gateway.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.test.web.reactive.server.WebTestClient;

@WebFluxTest(FallbackController.class)
class FallbackControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void testServiceFallback() {
        webTestClient.get()
                .uri("/fallback/test-service")
                .exchange()
                .expectStatus().isEqualTo(503)
                .expectBody()
                .jsonPath("$.status").isEqualTo("error")
                .jsonPath("$.service").isEqualTo("test-service")
                .jsonPath("$.fallback").isEqualTo(true)
                .jsonPath("$.message").exists();
    }

    @Test
    void testServiceFallbackWithDifferentService() {
        webTestClient.get()
                .uri("/fallback/another-service")
                .exchange()
                .expectStatus().isEqualTo(503)
                .expectBody()
                .jsonPath("$.service").isEqualTo("another-service");
    }
}

