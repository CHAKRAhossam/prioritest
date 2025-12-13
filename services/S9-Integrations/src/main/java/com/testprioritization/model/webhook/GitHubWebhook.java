package com.testprioritization.model.webhook;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GitHub webhook payload for pull request events.
 * Aligned with architecture specification.
 * 
 * Input format from architecture spec:
 * {
 *   "event": "pull_request",
 *   "action": "opened|synchronize",
 *   "pull_request": {
 *     "number": 123,
 *     "head": {
 *       "sha": "abc123",
 *       "ref": "feature/new-feature"
 *     },
 *     "files": [
 *       {"path": "src/UserService.java", "status": "modified"}
 *     ]
 *   }
 * }
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class GitHubWebhook {

    private String event;
    private String action;
    
    @JsonProperty("pull_request")
    private PullRequest pullRequest;
    
    private Repository repository;
    private Sender sender;
    private Installation installation;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class PullRequest {
        private Long id;
        private Integer number;
        private String state;
        private String title;
        private String body;
        private Head head;
        private Base base;
        private User user;
        
        @JsonProperty("changed_files")
        private Integer changedFiles;
        
        private Integer additions;
        private Integer deletions;
        private Integer commits;
        
        @JsonProperty("html_url")
        private String htmlUrl;
        
        @JsonProperty("diff_url")
        private String diffUrl;
        
        private Boolean draft;
        private Boolean merged;
        private Boolean mergeable;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Head {
        private String sha;
        private String ref;
        private Repository repo;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Base {
        private String sha;
        private String ref;
        private Repository repo;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Repository {
        private Long id;
        private String name;
        
        @JsonProperty("full_name")
        private String fullName;
        
        @JsonProperty("private")
        private Boolean isPrivate;
        
        private Owner owner;
        
        @JsonProperty("html_url")
        private String htmlUrl;
        
        @JsonProperty("clone_url")
        private String cloneUrl;
        
        @JsonProperty("default_branch")
        private String defaultBranch;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Owner {
        private Long id;
        private String login;
        private String type;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class User {
        private Long id;
        private String login;
        
        @JsonProperty("avatar_url")
        private String avatarUrl;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Sender {
        private Long id;
        private String login;
        private String type;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Installation {
        private Long id;
    }
}

