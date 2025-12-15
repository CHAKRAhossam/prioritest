package com.prioritest.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Additional route configuration using Java DSL.
 * This complements the YAML configuration for more complex routing logic.
 */
@Configuration
public class GatewayConfig {

    /**
     * Programmatic route definitions for special cases.
     * Most routes are defined in application.yml for easier management.
     */
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            // Aggregate health check endpoint
            .route("health-aggregate", r -> r
                .path("/health")
                .uri("forward:/api/health/all"))
            
            // API Documentation aggregation (if needed)
            .route("api-docs", r -> r
                .path("/api-docs/**")
                .filters(f -> f.stripPrefix(1))
                .uri("http://localhost:8080"))
            
            .build();
    }
}
