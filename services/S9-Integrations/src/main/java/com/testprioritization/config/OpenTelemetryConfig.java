package com.testprioritization.config;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.semconv.ResourceAttributes;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import lombok.extern.slf4j.Slf4j;

import java.time.Duration;

/**
 * OpenTelemetry configuration for distributed tracing and metrics.
 */
@Configuration
@Slf4j
public class OpenTelemetryConfig {

    @Value("${otel.service.name:cicd-integration-service}")
    private String serviceName;

    @Value("${otel.exporter.otlp.endpoint:http://localhost:4317}")
    private String otlpEndpoint;

    @Bean
    public Resource otelResource() {
        return Resource.getDefault()
                .merge(Resource.create(Attributes.of(
                        ResourceAttributes.SERVICE_NAME, serviceName,
                        ResourceAttributes.SERVICE_VERSION, "1.0.0",
                        ResourceAttributes.DEPLOYMENT_ENVIRONMENT, 
                            System.getenv().getOrDefault("ENVIRONMENT", "development")
                )));
    }

    @Bean
    public OtlpGrpcSpanExporter otlpSpanExporter() {
        return OtlpGrpcSpanExporter.builder()
                .setEndpoint(otlpEndpoint)
                .setTimeout(Duration.ofSeconds(10))
                .build();
    }

    @Bean
    public SdkTracerProvider sdkTracerProvider(Resource resource, OtlpGrpcSpanExporter spanExporter) {
        return SdkTracerProvider.builder()
                .addSpanProcessor(BatchSpanProcessor.builder(spanExporter)
                        .setMaxQueueSize(2048)
                        .setMaxExportBatchSize(512)
                        .setScheduleDelay(Duration.ofSeconds(5))
                        .build())
                .setResource(resource)
                .build();
    }

    @Bean
    public OtlpGrpcMetricExporter otlpMetricExporter() {
        return OtlpGrpcMetricExporter.builder()
                .setEndpoint(otlpEndpoint)
                .setTimeout(Duration.ofSeconds(10))
                .build();
    }

    @Bean
    public SdkMeterProvider sdkMeterProvider(Resource resource, OtlpGrpcMetricExporter metricExporter) {
        return SdkMeterProvider.builder()
                .registerMetricReader(PeriodicMetricReader.builder(metricExporter)
                        .setInterval(Duration.ofSeconds(60))
                        .build())
                .setResource(resource)
                .build();
    }

    @Bean
    public OpenTelemetry openTelemetry(SdkTracerProvider tracerProvider, SdkMeterProvider meterProvider) {
        OpenTelemetrySdk openTelemetry = OpenTelemetrySdk.builder()
                .setTracerProvider(tracerProvider)
                .setMeterProvider(meterProvider)
                .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
                .build();

        // Register as global (optional, for libraries that use GlobalOpenTelemetry)
        GlobalOpenTelemetry.set(openTelemetry);
        
        log.info("OpenTelemetry configured with endpoint: {}", otlpEndpoint);
        return openTelemetry;
    }

    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer(serviceName, "1.0.0");
    }

    @Bean
    public Meter meter(OpenTelemetry openTelemetry) {
        return openTelemetry.getMeter(serviceName);
    }
}

