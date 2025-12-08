package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "class_test_map", indexes = {
    @Index(name = "idx_map_class", columnList = "className"),
    @Index(name = "idx_map_test", columnList = "testName"),
    @Index(name = "idx_map_commit", columnList = "commitSha"),
    @Index(name = "idx_map_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class ClassTestMap {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String repositoryId;
    
    @Column(nullable = false)
    private String commitSha;
    
    @Column(nullable = false)
    private String className;
    
    @Column(nullable = false)
    private String testName;
    
    private double coveragePercent;
    
    // Detailed metrics for this class-test relationship
    private int linesCovered;
    private int totalLines;
    private int branchesCovered;
    private int totalBranches;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp = LocalDateTime.now();
}
