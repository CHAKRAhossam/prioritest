package com.example.historiquetests.service;

import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.GetObjectArgs;
import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.io.ByteArrayInputStream;

@Service
@Slf4j
public class MinioService {

    private final MinioClient minioClient;
    private final String bucket;

    public MinioService(@Value("${minio.url}") String url,
                        @Value("${minio.access-key}") String accessKey,
                        @Value("${minio.secret-key}") String secretKey,
                        @Value("${minio.bucket}") String bucket) {
        this.minioClient = MinioClient.builder().endpoint(url).credentials(accessKey, secretKey).build();
        this.bucket = bucket;
        initializeBucket();
    }

    private void initializeBucket() {
        try {
            boolean exists = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucket).build());
            if (!exists) {
                minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucket).build());
                log.info("Created bucket: {}", bucket);
            }
        } catch (Exception e) {
            log.warn("Could not initialize MinIO bucket: {}", e.getMessage());
        }
    }

    public String upload(String objectName, MultipartFile file) throws Exception {
        try (InputStream is = file.getInputStream()) {
            minioClient.putObject(PutObjectArgs.builder()
                    .bucket(bucket)
                    .object(objectName)
                    .stream(is, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build());
        }
        log.info("Uploaded file: {} to bucket: {}", objectName, bucket);
        return objectName;
    }
    
    /**
     * Download a file from MinIO
     * Supports both full URLs (s3://minio/bucket/path) and object names
     */
    public InputStream download(String artifactUrl) throws Exception {
        String objectName = parseObjectName(artifactUrl);
        String bucketName = parseBucketName(artifactUrl);
        
        log.info("Downloading from MinIO: bucket={}, object={}", bucketName, objectName);
        
        InputStream stream = minioClient.getObject(
            GetObjectArgs.builder()
                .bucket(bucketName)
                .object(objectName)
                .build()
        );
        
        // Read into byte array to avoid connection issues
        byte[] content = stream.readAllBytes();
        stream.close();
        
        log.info("Downloaded {} bytes from MinIO: {}", content.length, objectName);
        return new ByteArrayInputStream(content);
    }
    
    /**
     * Parse object name from artifact URL
     * Examples:
     * - s3://minio/artifacts/jacoco_abc123.xml -> jacoco_abc123.xml
     * - s3://minio/coverage-reports/commit123/jacoco.xml -> commit123/jacoco.xml
     * - jacoco.xml -> jacoco.xml
     */
    private String parseObjectName(String artifactUrl) {
        if (artifactUrl == null || artifactUrl.isEmpty()) {
            throw new IllegalArgumentException("Artifact URL cannot be null or empty");
        }
        
        // Handle s3:// URLs
        if (artifactUrl.startsWith("s3://")) {
            // s3://minio/bucket/path/to/file -> path/to/file
            String withoutProtocol = artifactUrl.substring(5); // Remove "s3://"
            int firstSlash = withoutProtocol.indexOf('/');
            if (firstSlash == -1) {
                throw new IllegalArgumentException("Invalid S3 URL format: " + artifactUrl);
            }
            String afterHost = withoutProtocol.substring(firstSlash + 1);
            int bucketSlash = afterHost.indexOf('/');
            if (bucketSlash == -1) {
                return afterHost; // Just bucket name, no path
            }
            return afterHost.substring(bucketSlash + 1);
        }
        
        // Handle http:// URLs
        if (artifactUrl.startsWith("http://") || artifactUrl.startsWith("https://")) {
            // Extract path after bucket
            String path = artifactUrl.replaceFirst("https?://[^/]+/[^/]+/", "");
            return path;
        }
        
        // Assume it's just an object name
        return artifactUrl;
    }
    
    /**
     * Parse bucket name from artifact URL
     */
    private String parseBucketName(String artifactUrl) {
        if (artifactUrl.startsWith("s3://")) {
            // s3://minio/bucket/path -> bucket
            String withoutProtocol = artifactUrl.substring(5);
            int firstSlash = withoutProtocol.indexOf('/');
            if (firstSlash == -1) {
                return bucket; // Default bucket
            }
            String afterHost = withoutProtocol.substring(firstSlash + 1);
            int bucketSlash = afterHost.indexOf('/');
            if (bucketSlash == -1) {
                return afterHost;
            }
            return afterHost.substring(0, bucketSlash);
        }
        
        // Default to configured bucket
        return bucket;
    }
}
