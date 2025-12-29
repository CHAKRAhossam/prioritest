package com.prioritest.gateway.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;
import org.springframework.web.cors.reactive.CorsWebFilter;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class CorsConfigTest {

    @Autowired
    private CorsConfig corsConfig;

    @Test
    void testCorsConfigBean() {
        assertNotNull(corsConfig);
    }

    @Test
    void testCorsWebFilterBean() {
        CorsWebFilter filter = corsConfig.corsWebFilter();
        assertNotNull(filter);
    }
}

