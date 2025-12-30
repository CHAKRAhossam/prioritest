package com.reco.analysestatiqueservice.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * DTO for Kafka messages to code.metrics topic.
 * Represents code metrics extracted for a class.
 * 
 * Format aligned with architecture specification:
 * {
 *   "event_id": "evt_126",
 *   "repository_id": "repo_12345",
 *   "commit_sha": "abc123",
 *   "class_name": "com.example.UserService",
 *   "file_path": "src/UserService.java",
 *   "metrics": {...},
 *   "timestamp": "2025-12-04T10:40:00Z"
 * }
 */
public class CodeMetricsEvent {
    
    @JsonProperty("event_id")
    private String eventId;
    
    @JsonProperty("repository_id")
    private String repositoryId;
    
    @JsonProperty("commit_sha")
    private String commitSha;
    
    @JsonProperty("class_name")
    private String className;
    
    @JsonProperty("file_path")
    private String filePath;
    
    @JsonProperty("metrics")
    private Metrics metrics;
    
    @JsonProperty("timestamp")
    private String timestamp;
    
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
    
    public String getClassName() {
        return className;
    }
    
    public void setClassName(String className) {
        this.className = className;
    }
    
    public String getFilePath() {
        return filePath;
    }
    
    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }
    
    public Metrics getMetrics() {
        return metrics;
    }
    
    public void setMetrics(Metrics metrics) {
        this.metrics = metrics;
    }
    
    public String getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    
    /**
     * Inner class for metrics structure.
     */
    public static class Metrics {
        @JsonProperty("loc")
        private Integer loc;
        
        @JsonProperty("cyclomatic_complexity")
        private Integer cyclomaticComplexity;
        
        @JsonProperty("ck_metrics")
        private CKMetrics ckMetrics;
        
        @JsonProperty("dependencies")
        private Dependencies dependencies;
        
        @JsonProperty("code_smells")
        private List<CodeSmell> codeSmells;
        
        // Getters and Setters
        public Integer getLoc() {
            return loc;
        }
        
        public void setLoc(Integer loc) {
            this.loc = loc;
        }
        
        public Integer getCyclomaticComplexity() {
            return cyclomaticComplexity;
        }
        
        public void setCyclomaticComplexity(Integer cyclomaticComplexity) {
            this.cyclomaticComplexity = cyclomaticComplexity;
        }
        
        public CKMetrics getCkMetrics() {
            return ckMetrics;
        }
        
        public void setCkMetrics(CKMetrics ckMetrics) {
            this.ckMetrics = ckMetrics;
        }
        
        public Dependencies getDependencies() {
            return dependencies;
        }
        
        public void setDependencies(Dependencies dependencies) {
            this.dependencies = dependencies;
        }
        
        public List<CodeSmell> getCodeSmells() {
            return codeSmells;
        }
        
        public void setCodeSmells(List<CodeSmell> codeSmells) {
            this.codeSmells = codeSmells;
        }
    }
    
    /**
     * Inner class for CK metrics.
     */
    public static class CKMetrics {
        @JsonProperty("wmc")
        private Integer wmc;
        
        @JsonProperty("dit")
        private Integer dit;
        
        @JsonProperty("noc")
        private Integer noc;
        
        @JsonProperty("cbo")
        private Integer cbo;
        
        @JsonProperty("rfc")
        private Integer rfc;
        
        @JsonProperty("lcom")
        private Double lcom;
        
        // Getters and Setters
        public Integer getWmc() {
            return wmc;
        }
        
        public void setWmc(Integer wmc) {
            this.wmc = wmc;
        }
        
        public Integer getDit() {
            return dit;
        }
        
        public void setDit(Integer dit) {
            this.dit = dit;
        }
        
        public Integer getNoc() {
            return noc;
        }
        
        public void setNoc(Integer noc) {
            this.noc = noc;
        }
        
        public Integer getCbo() {
            return cbo;
        }
        
        public void setCbo(Integer cbo) {
            this.cbo = cbo;
        }
        
        public Integer getRfc() {
            return rfc;
        }
        
        public void setRfc(Integer rfc) {
            this.rfc = rfc;
        }
        
        public Double getLcom() {
            return lcom;
        }
        
        public void setLcom(Double lcom) {
            this.lcom = lcom;
        }
    }
    
    /**
     * Inner class for dependencies.
     */
    public static class Dependencies {
        @JsonProperty("in_degree")
        private Integer inDegree;
        
        @JsonProperty("out_degree")
        private Integer outDegree;
        
        @JsonProperty("dependencies_list")
        private List<String> dependenciesList;
        
        // Getters and Setters
        public Integer getInDegree() {
            return inDegree;
        }
        
        public void setInDegree(Integer inDegree) {
            this.inDegree = inDegree;
        }
        
        public Integer getOutDegree() {
            return outDegree;
        }
        
        public void setOutDegree(Integer outDegree) {
            this.outDegree = outDegree;
        }
        
        public List<String> getDependenciesList() {
            return dependenciesList;
        }
        
        public void setDependenciesList(List<String> dependenciesList) {
            this.dependenciesList = dependenciesList;
        }
    }
    
    /**
     * Inner class for code smells.
     */
    public static class CodeSmell {
        @JsonProperty("type")
        private String type;
        
        @JsonProperty("severity")
        private String severity;
        
        @JsonProperty("line")
        private Integer line;
        
        // Getters and Setters
        public String getType() {
            return type;
        }
        
        public void setType(String type) {
            this.type = type;
        }
        
        public String getSeverity() {
            return severity;
        }
        
        public void setSeverity(String severity) {
            this.severity = severity;
        }
        
        public Integer getLine() {
            return line;
        }
        
        public void setLine(Integer line) {
            this.line = line;
        }
    }
}

