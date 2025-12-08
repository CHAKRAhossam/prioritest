package com.reco.analysestatiqueservice.extractor;

import com.reco.analysestatiqueservice.dto.FileScanResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for JavaParserExtractor.
 *
 * @author Reco Team
 */
class JavaParserExtractorTest {

    private JavaParserExtractor extractor;

    @BeforeEach
    void setUp() {
        extractor = new JavaParserExtractor();
    }

    @Test
    void testListJavaFilesDetailed(@TempDir Path tempDir) throws IOException {
        // Create a directory structure with Java files
        Path srcDir = tempDir.resolve("src/main/java");
        Files.createDirectories(srcDir);

        Files.writeString(srcDir.resolve("Main.java"), "public class Main {}");
        Files.writeString(srcDir.resolve("Utils.java"), "public class Utils {}");
        Files.writeString(tempDir.resolve("README.md"), "# Project");

        File projectDir = tempDir.toFile();
        List<FileScanResult> results = extractor.listJavaFilesDetailed(projectDir);

        assertEquals(2, results.size());
        // FileScanResult constructor: (path=fileName, className=absolutePath)
        assertTrue(results.stream().anyMatch(r -> r.getPath().equals("Main.java") || r.getClassName().contains("Main")));
        assertTrue(results.stream().anyMatch(r -> r.getPath().equals("Utils.java") || r.getClassName().contains("Utils")));
    }

    @Test
    void testListJavaFilesDetailedNoJavaFiles(@TempDir Path tempDir) throws IOException {
        // Create directory with no Java files
        Files.writeString(tempDir.resolve("README.md"), "# Project");
        Files.writeString(tempDir.resolve("pom.xml"), "<project></project>");

        File projectDir = tempDir.toFile();
        List<FileScanResult> results = extractor.listJavaFilesDetailed(projectDir);

        assertTrue(results.isEmpty());
    }

    @Test
    void testListJavaFilesDetailedNestedStructure(@TempDir Path tempDir) throws IOException {
        // Create nested directory structure
        Path packageDir = tempDir.resolve("src/main/java/com/example");
        Files.createDirectories(packageDir);

        Files.writeString(packageDir.resolve("Service.java"), "public class Service {}");
        Files.writeString(packageDir.resolve("Controller.java"), "public class Controller {}");

        File projectDir = tempDir.toFile();
        List<FileScanResult> results = extractor.listJavaFilesDetailed(projectDir);

        assertEquals(2, results.size());
    }
}

