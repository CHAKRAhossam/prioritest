package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "test_flakiness", indexes = {
    @Index(name = "idx_flakiness_test", columnList = "testClass,testName"),
    @Index(name = "idx_flakiness_score", columnList = "flakinessScore"),
    @Index(name = "idx_flakiness_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class TestFlakiness {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String repositoryId;
    
    @Column(nullable = false)
    private String testClass;
    
    @Column(nullable = false)
    private String testName;
    
    // Flakiness metrics
    private int totalRuns;
    private int failedRuns;
    private int passedRuns;
    private int consecutiveFailures;
    private double flakinessScore; // 0.0 (stable) to 1.0 (very flaky)
    
    // Time window for calculation
    private LocalDateTime windowStart;
    private LocalDateTime windowEnd;
    
    // Last status changes
    private LocalDateTime lastFailure;
    private LocalDateTime lastSuccess;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime calculatedAt = LocalDateTime.now();
}


