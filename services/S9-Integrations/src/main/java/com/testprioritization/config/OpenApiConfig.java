package com.testprioritization.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.License;
import io.swagger.v3.oas.annotations.security.OAuthFlow;
import io.swagger.v3.oas.annotations.security.OAuthFlows;
import io.swagger.v3.oas.annotations.security.OAuthScope;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.annotations.security.SecuritySchemes;
import io.swagger.v3.oas.annotations.servers.Server;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.media.Schema;
import io.swagger.v3.oas.models.responses.ApiResponse;
import io.swagger.v3.oas.models.responses.ApiResponses;
import org.springdoc.core.customizers.OpenApiCustomizer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Map;

/**
 * OpenAPI/Swagger configuration for the CI/CD Integration Service API.
 */
@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "CI/CD Integration Service API",
        version = "1.0.0",
        description = """
            ## Service d'intégration CI/CD pour l'analyse des risques et la priorisation des tests
            
            Ce service fournit les fonctionnalités suivantes:
            
            - **Webhooks GitHub/GitLab**: Réception et traitement des événements de Pull Requests / Merge Requests
            - **Analyse de risque**: Évaluation automatique du niveau de risque des modifications de code
            - **Policy Gate**: Vérification des politiques de qualité et blocage si nécessaire
            - **Entraînement ML**: Déclenchement et gestion des jobs d'entraînement des modèles
            - **Health Checks**: Endpoints de surveillance pour Kubernetes
            
            ### Authentification
            
            L'API utilise OAuth2/OpenID Connect via Keycloak. Les endpoints webhooks sont accessibles
            sans authentification (validation par signature/token). Les endpoints de gestion
            requièrent un token JWT valide.
            """,
        contact = @Contact(
            name = "DevOps Team",
            email = "devops@example.com",
            url = "https://github.com/test-prioritization"
        ),
        license = @License(
            name = "MIT License",
            url = "https://opensource.org/licenses/MIT"
        )
    ),
    servers = {
        @Server(url = "/api", description = "API Gateway"),
        @Server(url = "http://localhost:8080/api", description = "Local Development"),
        @Server(url = "https://api.example.com/api", description = "Production")
    },
    security = @SecurityRequirement(name = "bearer-jwt")
)
@SecuritySchemes({
    @SecurityScheme(
        name = "bearer-jwt",
        type = SecuritySchemeType.HTTP,
        scheme = "bearer",
        bearerFormat = "JWT",
        description = "JWT Token obtenu via Keycloak. Format: Bearer {token}"
    ),
    @SecurityScheme(
        name = "oauth2",
        type = SecuritySchemeType.OAUTH2,
        description = "OAuth2 via Keycloak",
        flows = @OAuthFlows(
            clientCredentials = @OAuthFlow(
                tokenUrl = "${KEYCLOAK_ISSUER_URI:http://localhost:8180/realms/cicd-integration}/protocol/openid-connect/token",
                scopes = {
                    @OAuthScope(name = "openid", description = "OpenID Connect scope"),
                    @OAuthScope(name = "profile", description = "User profile"),
                    @OAuthScope(name = "email", description = "User email")
                }
            ),
            authorizationCode = @OAuthFlow(
                authorizationUrl = "${KEYCLOAK_ISSUER_URI:http://localhost:8180/realms/cicd-integration}/protocol/openid-connect/auth",
                tokenUrl = "${KEYCLOAK_ISSUER_URI:http://localhost:8180/realms/cicd-integration}/protocol/openid-connect/token",
                scopes = {
                    @OAuthScope(name = "openid", description = "OpenID Connect scope"),
                    @OAuthScope(name = "profile", description = "User profile"),
                    @OAuthScope(name = "email", description = "User email")
                }
            )
        )
    )
})
public class OpenApiConfig {

    @Value("${spring.application.name:cicd-integration-service}")
    private String applicationName;

    /**
     * Customizer to add common API responses to all operations.
     */
    @Bean
    public OpenApiCustomizer globalResponsesCustomizer() {
        return openApi -> {
            openApi.getPaths().values().forEach(pathItem -> 
                pathItem.readOperations().forEach(operation -> {
                    ApiResponses responses = operation.getResponses();
                    
                    // Add common error responses if not already present
                    if (!responses.containsKey("401")) {
                        responses.addApiResponse("401", new ApiResponse()
                            .description("Non authentifié - Token JWT invalide ou manquant"));
                    }
                    if (!responses.containsKey("403")) {
                        responses.addApiResponse("403", new ApiResponse()
                            .description("Non autorisé - Permissions insuffisantes"));
                    }
                    if (!responses.containsKey("500")) {
                        responses.addApiResponse("500", new ApiResponse()
                            .description("Erreur interne du serveur"));
                    }
                })
            );
        };
    }

    /**
     * Additional OpenAPI customization for schemas and components.
     */
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .components(new Components()
                .addSchemas("ErrorResponse", new Schema<Map<String, Object>>()
                    .type("object")
                    .description("Standard error response")
                    .addProperty("error", new Schema<String>()
                        .type("string")
                        .description("Error message"))
                    .addProperty("timestamp", new Schema<String>()
                        .type("string")
                        .format("date-time")
                        .description("Error timestamp"))
                    .addProperty("path", new Schema<String>()
                        .type("string")
                        .description("Request path"))
                    .addProperty("status", new Schema<Integer>()
                        .type("integer")
                        .description("HTTP status code"))
                )
                .addSchemas("HealthResponse", new Schema<Map<String, Object>>()
                    .type("object")
                    .description("Health check response")
                    .addProperty("status", new Schema<String>()
                        .type("string")
                        .example("UP")
                        .description("Service status"))
                    .addProperty("timestamp", new Schema<String>()
                        .type("string")
                        .format("date-time")
                        .description("Check timestamp"))
                )
            );
    }
}

