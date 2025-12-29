package com.prioritest.gateway.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.test.web.reactive.server.WebTestClient;
import reactor.test.StepVerifier;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@WebFluxTest(HealthController.class)
class HealthControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void testGatewayHealth() {
        webTestClient.get()
                .uri("/api/health")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.status").isEqualTo("UP")
                .jsonPath("$.service").isEqualTo("api-gateway")
                .jsonPath("$.version").isEqualTo("1.0.0");
    }

    @Test
    void testAllServicesHealth() {
        webTestClient.get()
                .uri("/api/health/all")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.gateway").isEqualTo("UP")
                .jsonPath("$.services").exists();
    }

    @Test
    void testGetRoutes() {
        webTestClient.get()
                .uri("/api/health/routes")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.s1").exists()
                .jsonPath("$.s2").exists()
                .jsonPath("$.s3").exists()
                .jsonPath("$.s4").exists()
                .jsonPath("$.s5").exists()
                .jsonPath("$.s6").exists()
                .jsonPath("$.s7").exists()
                .jsonPath("$.s9").exists();
    }
}

