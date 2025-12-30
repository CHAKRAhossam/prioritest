package com.testprioritization.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import lombok.Data;

/**
 * Application configuration properties.
 */
@Data
@Validated
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private final GitHub github = new GitHub();
    private final GitLab gitlab = new GitLab();
    private final Risk risk = new Risk();
    private final PolicyGate policyGate = new PolicyGate();
    private final Training training = new Training();
    private final Prioritization prioritization = new Prioritization();
    private final Keycloak keycloak = new Keycloak();

    @Data
    public static class GitHub {
        private String appId;
        private String privateKey;
        private String webhookSecret;
        private String apiBaseUrl = "https://api.github.com";
    }

    @Data
    public static class GitLab {
        private String token;
        private String webhookSecret;
        private String apiBaseUrl = "https://gitlab.com/api/v4";
    }

    @Data
    public static class Risk {
        private Threshold threshold = new Threshold();

        @Data
        public static class Threshold {
            private double high = 0.7;
            private double medium = 0.4;
        }
    }

    @Data
    public static class PolicyGate {
        private boolean enabled = true;
        private boolean blockOnHighRisk = false;
        private boolean requireTestsForHighRisk = true;
    }

    @Data
    public static class Training {
        private String serviceUrl = "http://training-service:8001";
        private boolean enabled = true;
        private int minCommitsThreshold = 100;
        private String cron = "0 0 2 * * ?";
    }

    @Data
    public static class Prioritization {
        private String serviceUrl = "http://prioritization-service:8002";
    }

    @Data
    public static class Keycloak {
        private String serverUrl;
        private String realm;
        private String clientId;
        private String clientSecret;
    }
}

