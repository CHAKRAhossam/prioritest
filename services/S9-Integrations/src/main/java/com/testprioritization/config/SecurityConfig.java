package com.testprioritization.config;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import org.springframework.beans.factory.annotation.Value;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Security configuration with Keycloak OAuth2/OIDC integration.
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
@Slf4j
public class SecurityConfig {

    @Value("${spring.profiles.active:dev}")
    private String activeProfile;

    private static final String[] PUBLIC_ENDPOINTS = {
        "/actuator/**",
        "/api-docs/**",
        "/swagger-ui/**",
        "/swagger-ui.html",
        "/v1/webhooks/github",
        "/v1/webhooks/gitlab",
        "/v1/health/**",
        "/h2-console/**"
    };

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
        
        // For local or dev profile, permit all requests (no Keycloak required)
        if ("local".equals(activeProfile) || "dev".equals(activeProfile)) {
            log.info("Running in {} profile - security disabled for testing", activeProfile);
            http
                .authorizeHttpRequests(auth -> auth.anyRequest().permitAll())
                .headers(headers -> headers.frameOptions(frame -> frame.disable())); // For H2 console
        } else {
            http
                .authorizeHttpRequests(auth -> auth
                    .requestMatchers(PUBLIC_ENDPOINTS).permitAll()
                    .requestMatchers("/v1/admin/**").hasRole("ADMIN")
                    .requestMatchers("/v1/training/**").hasAnyRole("ADMIN", "TRAINING_MANAGER")
                    .anyRequest().authenticated()
                )
                .oauth2ResourceServer(oauth2 -> oauth2
                    .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter()))
                );
        }

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of("*"));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setExposedHeaders(List.of("Authorization", "X-Request-Id", "X-Trace-Id"));
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    /**
     * Custom JWT authentication converter to extract Keycloak roles.
     */
    @Bean
    public Converter<Jwt, AbstractAuthenticationToken> jwtAuthenticationConverter() {
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(new KeycloakRealmRoleConverter());
        return converter;
    }

    /**
     * Converter for Keycloak realm roles from JWT claims.
     */
    @SuppressWarnings({"unchecked", "null"})
    static class KeycloakRealmRoleConverter implements Converter<Jwt, Collection<GrantedAuthority>> {
        
        @Override
        public Collection<GrantedAuthority> convert(Jwt jwt) {
            // Extract realm_access roles
            Collection<GrantedAuthority> realmRoles = extractRealmRoles(jwt);
            
            // Extract resource_access (client) roles
            Collection<GrantedAuthority> resourceRoles = extractResourceRoles(jwt);
            
            return Stream.concat(realmRoles.stream(), resourceRoles.stream())
                    .collect(Collectors.toList());
        }

        private Collection<GrantedAuthority> extractRealmRoles(Jwt jwt) {
            Map<String, Object> realmAccess = jwt.getClaim("realm_access");
            if (realmAccess == null || !realmAccess.containsKey("roles")) {
                return List.of();
            }
            
            List<String> roles = (List<String>) realmAccess.get("roles");
            return roles.stream()
                    .map(role -> new SimpleGrantedAuthority("ROLE_" + role.toUpperCase()))
                    .collect(Collectors.toList());
        }

        private Collection<GrantedAuthority> extractResourceRoles(Jwt jwt) {
            Map<String, Object> resourceAccess = jwt.getClaim("resource_access");
            if (resourceAccess == null) {
                return List.of();
            }
            
            return resourceAccess.entrySet().stream()
                    .flatMap(entry -> {
                        Map<String, Object> clientAccess = (Map<String, Object>) entry.getValue();
                        if (clientAccess.containsKey("roles")) {
                            List<String> roles = (List<String>) clientAccess.get("roles");
                            return roles.stream()
                                    .map(role -> new SimpleGrantedAuthority(
                                            "ROLE_" + entry.getKey().toUpperCase() + "_" + role.toUpperCase()));
                        }
                        return Stream.empty();
                    })
                    .collect(Collectors.toList());
        }
    }
}

