package com.prioritest.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.Collections;

/**
 * CORS Configuration for the API Gateway.
 * Allows cross-origin requests from the frontend (S8-Dashboard).
 */
@Configuration
public class CorsConfig {

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfig = new CorsConfiguration();
        
        // Allow all origins in development - restrict in production
        corsConfig.setAllowedOrigins(Arrays.asList(
            "http://localhost:3000",        // React dev server
            "http://localhost:5173",        // Vite dev server
            "http://localhost:8080",        // Gateway itself
            "http://prioritest-dashboard:3000"  // Docker dashboard
        ));
        
        // Allow all common HTTP methods
        corsConfig.setAllowedMethods(Arrays.asList(
            "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
        ));
        
        // Allow all headers
        corsConfig.setAllowedHeaders(Collections.singletonList("*"));
        
        // Allow credentials (cookies, authorization headers)
        corsConfig.setAllowCredentials(true);
        
        // Cache preflight response for 1 hour
        corsConfig.setMaxAge(3600L);
        
        // Expose these headers to the client
        corsConfig.setExposedHeaders(Arrays.asList(
            "Authorization",
            "X-Request-Id",
            "X-Correlation-Id"
        ));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}
