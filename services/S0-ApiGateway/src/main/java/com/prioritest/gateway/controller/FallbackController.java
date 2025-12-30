package com.prioritest.gateway.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Fallback controller for circuit breaker failures.
 * Provides graceful degradation when services are unavailable.
 */
@RestController
@RequestMapping("/fallback")
public class FallbackController {

    private static final Logger log = LoggerFactory.getLogger(FallbackController.class);

    @GetMapping("/{service}")
    public Mono<ResponseEntity<Map<String, Object>>> serviceFallback(@PathVariable String service) {
        log.warn("Fallback triggered for service: {}", service);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("service", service);
        response.put("message", String.format("Service %s is currently unavailable. Please try again later.", service.toUpperCase()));
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("fallback", true);
        
        return Mono.just(ResponseEntity
            .status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(response));
    }
}
