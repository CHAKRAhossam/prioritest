package com.reco.analysestatiqueservice.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration conditionnelle pour la base de données.
 * JPA ne sera activé que si spring.datasource.url est configuré.
 */
@Configuration
@ConditionalOnProperty(name = "spring.datasource.url")
public class DatabaseConfig {
    // JPA sera activé automatiquement si la propriété est présente
}

