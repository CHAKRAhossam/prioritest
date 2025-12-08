package com.example.historiquetests.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * DTO for Kafka artifact events from topic: ci.artifacts
 * 
 * Example message:
 * {
 *   "event_id": "evt_125",
 *   "repository_id": "repo_12345",
 *   "build_id": "build_789",
 *   "commit_sha": "abc123",
 *   "artifact_type": "jacoco",
 *   "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml"
 * }
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ArtifactEvent {
    
    @JsonProperty("event_id")
    private String eventId;
    
    @JsonProperty("repository_id")
    private String repositoryId;
    
    @JsonProperty("build_id")
    private String buildId;
    
    @JsonProperty("commit_sha")
    private String commitSha;
    
    @JsonProperty("artifact_type")
    private String artifactType;
    
    @JsonProperty("artifact_url")
    private String artifactUrl;
    
    @JsonProperty("branch")
    private String branch;
    
    /**
     * Validate that this event has all required fields
     */
    public boolean isValid() {
        return repositoryId != null && !repositoryId.isEmpty() &&
               commitSha != null && !commitSha.isEmpty() &&
               artifactType != null && !artifactType.isEmpty() &&
               artifactUrl != null && !artifactUrl.isEmpty();
    }
    
    /**
     * Check if this is a JaCoCo artifact
     */
    public boolean isJaCoCo() {
        return "jacoco".equalsIgnoreCase(artifactType);
    }
    
    /**
     * Check if this is a Surefire artifact
     */
    public boolean isSurefire() {
        return "surefire".equalsIgnoreCase(artifactType);
    }
    
    /**
     * Check if this is a PIT artifact
     */
    public boolean isPIT() {
        return "pit".equalsIgnoreCase(artifactType) || 
               "pitest".equalsIgnoreCase(artifactType) ||
               "mutation".equalsIgnoreCase(artifactType);
    }
}


