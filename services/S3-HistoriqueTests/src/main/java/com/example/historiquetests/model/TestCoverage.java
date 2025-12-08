package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "test_coverage", indexes = {
    @Index(name = "idx_coverage_class", columnList = "className"),
    @Index(name = "idx_coverage_commit", columnList = "commitSha"),
    @Index(name = "idx_coverage_timestamp", columnList = "timestamp"),
    @Index(name = "idx_coverage_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class TestCoverage {

    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String repositoryId;
    
    @Column(nullable = false)
    private String commitSha;
    
    @Column(nullable = false)
    private String className;
    
    private String filePath;
    private String packageName;

    // Line coverage metrics
    private int linesCovered;
    private int linesMissed;
    
    // Branch coverage metrics
    private int branchesCovered;
    private int branchesMissed;
    
    // Method coverage metrics
    private int methodsCovered;
    private int methodsMissed;
    
    // Instruction coverage metrics (for JaCoCo)
    private int instructionsCovered;
    private int instructionsMissed;

    // Calculated percentages
    private double lineCoverage;
    private double branchCoverage;
    private double methodCoverage;
    private double instructionCoverage;

    // PIT mutation testing score
    private Double mutationScore;
    private Integer mutationsKilled;
    private Integer mutationsSurvived;
    private Integer mutationsNoCoverage;

    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp = LocalDateTime.now();
    
    // Build/CI metadata
    private String buildId;
    private String branch;
}
