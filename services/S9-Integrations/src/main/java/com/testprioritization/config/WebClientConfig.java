package com.testprioritization.config;

import java.time.Duration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.ExchangeFilterFunction;
import org.springframework.web.reactive.function.client.WebClient;

import io.netty.channel.ChannelOption;
import io.netty.handler.timeout.ReadTimeoutHandler;
import io.netty.handler.timeout.WriteTimeoutHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;

/**
 * WebClient configuration for external API calls.
 */
@Configuration
@RequiredArgsConstructor
@Slf4j
@SuppressWarnings("null")
public class WebClientConfig {

    private final AppProperties appProperties;

    @Bean
    public WebClient githubWebClient() {
        return createWebClient(appProperties.getGithub().getApiBaseUrl(), "GitHub");
    }

    @Bean
    public WebClient gitlabWebClient() {
        return createWebClient(appProperties.getGitlab().getApiBaseUrl(), "GitLab");
    }

    @Bean
    public WebClient trainingWebClient() {
        return createWebClient(appProperties.getTraining().getServiceUrl(), "Training");
    }

    @Bean
    public WebClient prioritizationWebClient() {
        return createWebClient(appProperties.getPrioritization().getServiceUrl(), "Prioritization");
    }

    private WebClient createWebClient(String baseUrl, String clientName) {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 10000)
                .responseTimeout(Duration.ofSeconds(30))
                .doOnConnected(conn -> conn
                        .addHandlerLast(new ReadTimeoutHandler(30))
                        .addHandlerLast(new WriteTimeoutHandler(30)));

        return WebClient.builder()
                .baseUrl(baseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
                .filter(logRequest(clientName))
                .filter(logResponse(clientName))
                .build();
    }

    private ExchangeFilterFunction logRequest(String clientName) {
        return ExchangeFilterFunction.ofRequestProcessor(request -> {
            log.debug("[{}] Request: {} {}", clientName, request.method(), request.url());
            return Mono.just(request);
        });
    }

    private ExchangeFilterFunction logResponse(String clientName) {
        return ExchangeFilterFunction.ofResponseProcessor(response -> {
            log.debug("[{}] Response: {}", clientName, response.statusCode());
            return Mono.just(response);
        });
    }
}

