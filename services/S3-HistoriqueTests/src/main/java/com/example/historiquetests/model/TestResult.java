package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "test_result", indexes = {
    @Index(name = "idx_result_test", columnList = "testClass,testName"),
    @Index(name = "idx_result_commit", columnList = "commitSha"),
    @Index(name = "idx_result_timestamp", columnList = "timestamp"),
    @Index(name = "idx_result_status", columnList = "status"),
    @Index(name = "idx_result_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class TestResult {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String repositoryId;

    @Column(nullable = false)
    private String commitSha;
    
    @Column(nullable = false)
    private String testName;
    
    @Column(nullable = false)
    private String testClass;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TestStatus status;
    
    private double executionTime; // in seconds

    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    
    @Column(columnDefinition = "TEXT")
    private String stackTrace;

    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp = LocalDateTime.now();
    
    // Additional metadata
    private String buildId;
    private String branch;
    private Integer retryCount;
    
    public enum TestStatus {
        PASSED, FAILED, SKIPPED, ERROR
    }
}
