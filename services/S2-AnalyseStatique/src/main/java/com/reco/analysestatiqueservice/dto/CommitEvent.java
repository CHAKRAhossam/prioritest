package com.reco.analysestatiqueservice.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * DTO for Kafka messages from repository.commits topic.
 * Represents a commit event with changed files.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class CommitEvent {
    
    @JsonProperty("event_id")
    private String eventId;
    
    @JsonProperty("repository_id")
    private String repositoryId;
    
    @JsonProperty("commit_sha")
    private String commitSha;
    
    @JsonProperty("commit_message")
    private String commitMessage;
    
    @JsonProperty("author_email")
    private String authorEmail;
    
    @JsonProperty("author_name")
    private String authorName;
    
    @JsonProperty("timestamp")
    private String timestamp;
    
    @JsonProperty("files_changed")
    private List<FileChanged> filesChanged;
    
    @JsonProperty("metadata")
    private Map<String, Object> metadata;
    
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
    
    public String getCommitMessage() {
        return commitMessage;
    }
    
    public void setCommitMessage(String commitMessage) {
        this.commitMessage = commitMessage;
    }
    
    public String getAuthorEmail() {
        return authorEmail;
    }
    
    public void setAuthorEmail(String authorEmail) {
        this.authorEmail = authorEmail;
    }
    
    public String getAuthorName() {
        return authorName;
    }
    
    public void setAuthorName(String authorName) {
        this.authorName = authorName;
    }
    
    public String getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    
    public Map<String, Object> getMetadata() {
        return metadata;
    }
    
    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }
    
    /**
     * Inner class for file change information.
     */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class FileChanged {
        private String path;
        private String status; // "added", "modified", "deleted"
        private Integer additions;
        private Integer deletions;
        
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
        
        public Integer getAdditions() {
            return additions;
        }
        
        public void setAdditions(Integer additions) {
            this.additions = additions;
        }
        
        public Integer getDeletions() {
            return deletions;
        }
        
        public void setDeletions(Integer deletions) {
            this.deletions = deletions;
        }
    }
}
