package com.prioritest.gateway.filter;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.mock.http.server.reactive.MockServerHttpRequest;
import org.springframework.mock.http.server.reactive.MockServerHttpResponse;
import org.springframework.mock.web.server.MockServerWebExchange;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class LoggingFilterTest {

    private LoggingFilter loggingFilter;
    private GatewayFilterChain filterChain;
    private ServerWebExchange exchange;

    @BeforeEach
    void setUp() {
        loggingFilter = new LoggingFilter();
        filterChain = mock(GatewayFilterChain.class);
    }

    @Test
    void testFilterWithCorrelationId() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/test")
                .header("X-Correlation-Id", "existing-correlation-id")
                .build();
        
        MockServerHttpResponse response = new MockServerHttpResponse();
        exchange = MockServerWebExchange.from(request);
        exchange.getResponse().setStatusCode(HttpStatus.OK);

        when(filterChain.filter(any(ServerWebExchange.class)))
                .thenReturn(Mono.empty());

        Mono<Void> result = loggingFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(filterChain).filter(any(ServerWebExchange.class));
    }

    @Test
    void testFilterWithoutCorrelationId() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/test")
                .build();
        
        MockServerHttpResponse response = new MockServerHttpResponse();
        exchange = MockServerWebExchange.from(request);
        exchange.getResponse().setStatusCode(HttpStatus.OK);

        when(filterChain.filter(any(ServerWebExchange.class)))
                .thenReturn(Mono.empty());

        Mono<Void> result = loggingFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(filterChain).filter(any(ServerWebExchange.class));
    }

    @Test
    void testGetOrder() {
        int order = loggingFilter.getOrder();
        assertEquals(Integer.MIN_VALUE, order); // HIGHEST_PRECEDENCE
    }
}

