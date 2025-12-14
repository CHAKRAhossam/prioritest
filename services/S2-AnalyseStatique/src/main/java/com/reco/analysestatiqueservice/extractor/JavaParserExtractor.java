package com.reco.analysestatiqueservice.extractor;

import com.reco.analysestatiqueservice.dto.FileScanResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/**
 * Extractor for discovering Java files in a project directory.
 *
 * @author Reco Team
 */
@Component
public class JavaParserExtractor {

    private static final Logger logger = LoggerFactory.getLogger(JavaParserExtractor.class);

    /**
     * Recursively lists all Java files in a directory.
     *
     * @param dir The root directory to search
     * @return List of Java files found
     */
    public List<File> listJavaFiles(File dir) {
        List<File> result = new ArrayList<>();
        File[] files = dir.listFiles();

        if (files == null) {
            return result;
        }

        for (File f : files) {
            if (f.isDirectory()) {
                result.addAll(listJavaFiles(f));
            } else if (f.getName().endsWith(".java")) {
                result.add(f);
            }
        }
        return result;
    }

    /**
     * Discovers all Java files in a project directory and returns detailed information.
     *
     * @param projectDir The root directory of the project
     * @return List of FileScanResult containing file information
     */
    public List<FileScanResult> listJavaFilesDetailed(File projectDir) {
        logger.debug("Scanning for Java files in: {}", projectDir.getAbsolutePath());
        List<FileScanResult> results = new ArrayList<>();
        Path projectPath = projectDir.toPath();

        try (Stream<Path> walk = Files.walk(projectPath)) {
            walk.filter(p -> p.toString().endsWith(".java"))
                    .filter(Files::isRegularFile)
                    .forEach(p -> {
                        // Calculate relative path from project root
                        Path relativePath = projectPath.relativize(p);
                        results.add(new FileScanResult(
                                relativePath.toString(),
                                p.toAbsolutePath().toString()
                        ));
                    });
        } catch (Exception e) {
            logger.error("Error scanning for Java files in: {}", projectDir.getAbsolutePath(), e);
            throw new RuntimeException("Failed to scan Java files", e);
        }

        logger.debug("Found {} Java files", results.size());
        return results;
    }
}
