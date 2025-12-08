package com.reco.analysestatiqueservice.extractor;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Utility class for extracting compressed projects (ZIP) to a clean temporary directory.
 * Excludes build artifacts, IDE files, and version control directories.
 *
 * @author Reco Team
 */
@Component
public class ZipExtractor {

    private static final Logger logger = LoggerFactory.getLogger(ZipExtractor.class);

    /**
     * Directories to exclude from extraction (build artifacts, IDE files, etc.)
     */
    private static final String[] EXCLUDED_DIRS = {
            "__MACOSX",
            ".git",
            ".idea",
            "target",
            "build",
            "out",
            ".gradle",
            ".mvn",
            "node_modules",
            ".svn",
            ".hg"
    };

    /**
     * Extracts a ZIP file to a temporary directory, excluding build artifacts and IDE files.
     *
     * @param zipFile The multipart ZIP file to extract
     * @return File pointing to the temporary directory containing extracted files
     * @throws IOException if extraction fails or security issues are detected
     */
    public File extractToTempDir(MultipartFile zipFile) throws IOException {
        logger.debug("Extracting ZIP file: {}", zipFile.getOriginalFilename());

        Path tempDir = Files.createTempDirectory("ms-analyse-");
        int extractedFiles = 0;

        try (ZipInputStream zis = new ZipInputStream(zipFile.getInputStream())) {
            ZipEntry entry;

            while ((entry = zis.getNextEntry()) != null) {
                // Skip directory entries
                if (entry.isDirectory()) {
                    continue;
                }

                // Normalize path (handle Windows/Unix differences)
                String entryName = entry.getName().replace('\\', '/');

                // Filter excluded directories
                if (isExcluded(entryName)) {
                    logger.debug("Excluding entry: {}", entryName);
                    continue;
                }

                // Resolve final path in temporary directory
                Path filePath = tempDir.resolve(entryName).normalize();

                // Security: prevent Zip Slip attack
                if (!filePath.startsWith(tempDir)) {
                    logger.error("Zip Slip attack detected for entry: {}", entryName);
                    throw new IOException("Invalid ZIP entry path detected: " + entryName);
                }

                // Create parent directories if needed
                Files.createDirectories(filePath.getParent());

                // Copy file content
                Files.copy(zis, filePath, StandardCopyOption.REPLACE_EXISTING);
                extractedFiles++;
            }
        }

        logger.info("Extracted {} files to temporary directory: {}", extractedFiles, tempDir);
        return tempDir.toFile();
    }

    /**
     * Checks if a path should be excluded from extraction.
     *
     * @param path The path to check
     * @return true if the path should be excluded, false otherwise
     */
    private boolean isExcluded(String path) {
        for (String excluded : EXCLUDED_DIRS) {
            if (path.startsWith(excluded + "/") || path.contains("/" + excluded + "/")) {
                return true;
            }
        }
        return false;
    }
}
