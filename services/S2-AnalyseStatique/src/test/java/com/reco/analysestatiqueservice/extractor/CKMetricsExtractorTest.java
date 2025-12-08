package com.reco.analysestatiqueservice.extractor;

import com.reco.analysestatiqueservice.model.ClassMetrics;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for CKMetricsExtractor.
 *
 * @author Reco Team
 */
class CKMetricsExtractorTest {

    private CKMetricsExtractor extractor;

    @BeforeEach
    void setUp() {
        extractor = new CKMetricsExtractor();
    }

    @Test
    void testExtractSimpleClass(@TempDir Path tempDir) throws IOException {
        // Create a simple Java class file
        String javaCode = """
                package com.example;
                
                public class SimpleClass {
                    private int value;
                    
                    public int getValue() {
                        return value;
                    }
                    
                    public void setValue(int value) {
                        this.value = value;
                    }
                }
                """;

        File javaFile = tempDir.resolve("SimpleClass.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        // Extract metrics
        ClassMetrics metrics = extractor.extract(javaFile);

        // Assertions
        assertNotNull(metrics);
        assertEquals("SimpleClass", metrics.getClassName());
        assertTrue(metrics.getLoc() > 0);
        assertEquals(2, metrics.getMethodsCount()); // getValue + setValue
        assertEquals(1, metrics.getAttributesCount()); // value
        assertTrue(metrics.getWmc() > 0); // At least base complexity
    }

    @Test
    void testExtractClassWithComplexity(@TempDir Path tempDir) throws IOException {
        // Create a class with higher complexity
        String javaCode = """
                package com.example;
                
                public class ComplexClass {
                    public void complexMethod(int x) {
                        if (x > 0) {
                            for (int i = 0; i < x; i++) {
                                if (i % 2 == 0) {
                                    System.out.println(i);
                                }
                            }
                        }
                    }
                }
                """;

        File javaFile = tempDir.resolve("ComplexClass.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        ClassMetrics metrics = extractor.extract(javaFile);

        assertNotNull(metrics);
        assertTrue(metrics.getWmc() > 1); // Should have complexity > 1 due to if/for
    }

    @Test
    void testExtractEmptyFile(@TempDir Path tempDir) throws IOException {
        File javaFile = tempDir.resolve("Empty.java").toFile();
        Files.writeString(javaFile.toPath(), "");

        ClassMetrics metrics = extractor.extract(javaFile);

        assertNotNull(metrics);
        assertEquals(0, metrics.getLoc());
    }

    @Test
    void testExtractNonExistentFile() {
        File nonExistent = new File("non-existent-file.java");

        assertThrows(IOException.class, () -> extractor.extract(nonExistent));
    }
}


