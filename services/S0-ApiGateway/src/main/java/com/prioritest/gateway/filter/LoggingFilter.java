package com.prioritest.gateway.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

/**
 * Global logging filter for request/response tracking.
 * Adds correlation ID and logs all incoming requests.
 */
@Component
public class LoggingFilter implements GlobalFilter, Ordered {

    private static final Logger log = LoggerFactory.getLogger(LoggingFilter.class);

    private static final String CORRELATION_ID_HEADER = "X-Correlation-Id";
    private static final String REQUEST_ID_HEADER = "X-Request-Id";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // Generate correlation ID if not present
        String correlationId = request.getHeaders().getFirst(CORRELATION_ID_HEADER);
        if (correlationId == null || correlationId.isEmpty()) {
            correlationId = UUID.randomUUID().toString();
        }
        
        // Generate request ID
        String requestId = UUID.randomUUID().toString().substring(0, 8);
        
        // Log incoming request
        log.info("[{}] {} {} - Path: {} - Client: {}",
            requestId,
            request.getMethod(),
            request.getURI().getPath(),
            request.getURI(),
            request.getRemoteAddress()
        );

        // Add headers to the request
        final String finalCorrelationId = correlationId;
        ServerHttpRequest modifiedRequest = request.mutate()
            .header(CORRELATION_ID_HEADER, finalCorrelationId)
            .header(REQUEST_ID_HEADER, requestId)
            .build();

        long startTime = System.currentTimeMillis();

        return chain.filter(exchange.mutate().request(modifiedRequest).build())
            .then(Mono.fromRunnable(() -> {
                long duration = System.currentTimeMillis() - startTime;
                log.info("[{}] Response: {} - Duration: {}ms",
                    requestId,
                    exchange.getResponse().getStatusCode(),
                    duration
                );
            }));
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
