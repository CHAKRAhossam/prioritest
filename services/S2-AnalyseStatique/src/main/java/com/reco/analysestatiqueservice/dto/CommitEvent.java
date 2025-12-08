package com.reco.analysestatiqueservice.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * DTO for Kafka messages from repository.commits topic.
 * Represents a commit event with changed files.
 */
public class CommitEvent {
    
    @JsonProperty("event_id")
    private String eventId;
    
    @JsonProperty("repository_id")
    private String repositoryId;
    
    @JsonProperty("commit_sha")
    private String commitSha;
    
    @JsonProperty("files_changed")
    private List<FileChanged> filesChanged;
    
    // Getters and Setters
    public String getEventId() {
        return eventId;
    }
    
    public void setEventId(String eventId) {
        this.eventId = eventId;
    }
    
    public String getRepositoryId() {
        return repositoryId;
    }
    
    public void setRepositoryId(String repositoryId) {
        this.repositoryId = repositoryId;
    }
    
    public String getCommitSha() {
        return commitSha;
    }
    
    public void setCommitSha(String commitSha) {
        this.commitSha = commitSha;
    }
    
    public List<FileChanged> getFilesChanged() {
        return filesChanged;
    }
    
    public void setFilesChanged(List<FileChanged> filesChanged) {
        this.filesChanged = filesChanged;
    }
    
    /**
     * Inner class for file change information.
     */
    public static class FileChanged {
        private String path;
        private String status; // "added", "modified", "deleted"
        
        public String getPath() {
            return path;
        }
        
        public void setPath(String path) {
            this.path = path;
        }
        
        public String getStatus() {
            return status;
        }
        
        public void setStatus(String status) {
            this.status = status;
        }
    }
}

