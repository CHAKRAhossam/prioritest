package com.testprioritization.model.webhook;

/**
 * GitLab webhook payload aligned with architecture specification.
 * 
 * Input format from architecture spec:
 * {
 *   "event_type": "merge_request",
 *   "object_attributes": {
 *     "iid": 45,
 *     "source_branch": "feature/new-feature",
 *     "last_commit": {
 *       "id": "abc123"
 *     }
 *   }
 * }
 */

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GitLab webhook payload for merge request events.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class GitLabWebhook {

    @JsonProperty("object_kind")
    private String objectKind;
    
    @JsonProperty("event_type")
    private String eventType;
    
    private User user;
    private Project project;
    
    @JsonProperty("object_attributes")
    private ObjectAttributes objectAttributes;
    
    private Labels labels;
    private Changes changes;
    private Repository repository;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class User {
        private Long id;
        private String name;
        private String username;
        private String email;
        
        @JsonProperty("avatar_url")
        private String avatarUrl;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Project {
        private Long id;
        private String name;
        private String description;
        
        @JsonProperty("web_url")
        private String webUrl;
        
        @JsonProperty("git_ssh_url")
        private String gitSshUrl;
        
        @JsonProperty("git_http_url")
        private String gitHttpUrl;
        
        private String namespace;
        
        @JsonProperty("visibility_level")
        private Integer visibilityLevel;
        
        @JsonProperty("path_with_namespace")
        private String pathWithNamespace;
        
        @JsonProperty("default_branch")
        private String defaultBranch;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ObjectAttributes {
        private Long id;
        private Long iid;
        private String title;
        private String description;
        private String state;
        
        @JsonProperty("source_branch")
        private String sourceBranch;
        
        @JsonProperty("target_branch")
        private String targetBranch;
        
        @JsonProperty("source_project_id")
        private Long sourceProjectId;
        
        @JsonProperty("target_project_id")
        private Long targetProjectId;
        
        @JsonProperty("author_id")
        private Long authorId;
        
        @JsonProperty("assignee_id")
        private Long assigneeId;
        
        @JsonProperty("merge_status")
        private String mergeStatus;
        
        @JsonProperty("merge_commit_sha")
        private String mergeCommitSha;
        
        @JsonProperty("last_commit")
        private LastCommit lastCommit;
        
        @JsonProperty("work_in_progress")
        private Boolean workInProgress;
        
        private Boolean draft;
        private String action;
        private String url;
        
        @JsonProperty("created_at")
        private String createdAt;
        
        @JsonProperty("updated_at")
        private String updatedAt;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class LastCommit {
        private String id;
        private String message;
        private String title;
        private String timestamp;
        private String url;
        private Author author;

        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Author {
            private String name;
            private String email;
        }
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Labels {
        private List<Label> previous;
        private List<Label> current;

        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Label {
            private Long id;
            private String title;
            private String color;
            private String description;
        }
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Changes {
        @JsonProperty("updated_at")
        private Change updatedAt;
        
        private Change title;
        private Change description;
        
        @JsonProperty("merge_status")
        private Change mergeStatus;

        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Change {
            private String previous;
            private String current;
        }
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Repository {
        private String name;
        private String url;
        private String description;
        private String homepage;
    }
}

