package com.reco.analysestatiqueservice.controller;

import com.reco.analysestatiqueservice.dto.MetricsResponse;
import com.reco.analysestatiqueservice.service.MetricsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * REST controller for code metrics analysis.
 * Provides endpoints for analyzing Java projects and extracting code metrics.
 *
 * @author Reco Team
 */
@RestController
@RequestMapping("/metrics")
@Validated
public class MetricsController {

    private static final Logger logger = LoggerFactory.getLogger(MetricsController.class);

    private final MetricsService metricsService;

    /**
     * Constructor with dependency injection.
     *
     * @param metricsService The service for metrics extraction
     */
    public MetricsController(MetricsService metricsService) {
        this.metricsService = metricsService;
    }

    /**
     * Analyzes a Java project from a ZIP file and returns code metrics.
     *
     * @param projectZip The ZIP file containing the Java project
     * @return ResponseEntity containing MetricsResponse with all extracted metrics
     */
    @PostMapping(
            path = "/analyze",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<MetricsResponse> analyzeProject(
            @RequestParam("file") MultipartFile projectZip) {

        logger.info("Received analysis request for file: {}", projectZip.getOriginalFilename());

        try {
            MetricsResponse response = metricsService.analyzeProject(projectZip);
            logger.info("Analysis completed successfully for file: {}", projectZip.getOriginalFilename());
            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            logger.error("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().build();

        } catch (Exception e) {
            logger.error("Error analyzing project: {}", projectZip.getOriginalFilename(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
