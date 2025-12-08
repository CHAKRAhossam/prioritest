package com.reco.analysestatiqueservice.extractor;

import com.reco.analysestatiqueservice.model.SmellResult;
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
 * Unit tests for SmellDetector.
 *
 * @author Reco Team
 */
class SmellDetectorTest {

    private SmellDetector detector;

    @BeforeEach
    void setUp() {
        detector = new SmellDetector();
    }

    @Test
    void testDetectGodClass(@TempDir Path tempDir) throws IOException {
        // Create a God Class (high LOC, WMC, CBO)
        StringBuilder code = new StringBuilder();
        code.append("package com.example;\n");
        code.append("public class GodClass {\n");
        
        // Add many fields
        for (int i = 0; i < 20; i++) {
            code.append("    private String field").append(i).append(";\n");
        }
        
        // Add many methods with complexity
        for (int i = 0; i < 30; i++) {
            code.append("    public void method").append(i).append("() {\n");
            code.append("        if (true) {\n");
            code.append("            for (int j = 0; j < 10; j++) {\n");
            code.append("                System.out.println(j);\n");
            code.append("            }\n");
            code.append("        }\n");
            code.append("    }\n");
        }
        
        code.append("}\n");

        File javaFile = tempDir.resolve("GodClass.java").toFile();
        Files.writeString(javaFile.toPath(), code.toString());

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // On attend au moins un God Class
        assertTrue(smells.stream().anyMatch(s -> s.getSmellType().equals("God Class")), "God Class should be detected");
    }

    @Test
    void testDetectLongMethod(@TempDir Path tempDir) throws IOException {
        String javaCode = """
                package com.example;
                
                public class Service {
                    public void longMethod() {
                        // Line 1
                        // Line 2
                        // Line 3
                        // ... many lines ...
                        // Line 50
                        // Line 51
                        // Line 52
                        // Line 53
                        // Line 54
                        // Line 55
                        // Line 56
                        // Line 57
                        // Line 58
                        // Line 59
                        // Line 60
                    }
                }
                """;

        File javaFile = tempDir.resolve("Service.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // Long Method doit être détecté
        assertTrue(smells.stream().anyMatch(s -> s.getSmellType().equals("Long Method")), "Long Method should be detected");
    }

    @Test
    void testDetectLongParameterList(@TempDir Path tempDir) throws IOException {
        String javaCode = """
                package com.example;
                
                public class Controller {
                    public void methodWithManyParams(String p1, String p2, String p3, 
                                                      String p4, String p5, String p6, 
                                                      String p7) {
                        // method body
                    }
                }
                """;

        File javaFile = tempDir.resolve("Controller.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // Long Parameter List doit être détecté
        assertTrue(smells.stream().anyMatch(s -> s.getSmellType().equals("Long Parameter List")), "Long Parameter List should be detected");
    }

    @Test
    void testDetectDataClass(@TempDir Path tempDir) throws IOException {
        String javaCode = """
                package com.example;
                
                public class User {
                    private String name;
                    private int age;
                    
                    public String getName() {
                        return name;
                    }
                    
                    public void setName(String name) {
                        this.name = name;
                    }
                    
                    public int getAge() {
                        return age;
                    }
                    
                    public void setAge(int age) {
                        this.age = age;
                    }
                }
                """;

        File javaFile = tempDir.resolve("User.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // Data Class doit être détecté
        assertTrue(smells.stream().anyMatch(s -> s.getSmellType().equals("Data Class")), "Data Class should be detected");
    }

    @Test
    void testDetectFeatureEnvy(@TempDir Path tempDir) throws IOException {
        String javaCode = """
                package com.example;
                
                public class Service {
                    private UserRepository userRepo;
                    private EmailService emailService;
                    private Logger logger;
                    
                    public void processUser(User user) {
                        // Many external calls
                        userRepo.save(user);
                        emailService.sendEmail(user.getEmail());
                        logger.info("Processing user");
                        emailService.notify(user);
                        userRepo.update(user);
                    }
                }
                """;

        File javaFile = tempDir.resolve("Service.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // Feature Envy doit être détecté
        assertTrue(smells.stream().anyMatch(s -> s.getSmellType().equals("Feature Envy")), "Feature Envy should be detected");
    }

    @Test
    void testDetectNoSmells(@TempDir Path tempDir) throws IOException {
        String javaCode = """
                package com.example;
                
                public class SimpleClass {
                    public void simpleMethod() {
                        System.out.println("Hello");
                    }
                }
                """;

        File javaFile = tempDir.resolve("SimpleClass.java").toFile();
        Files.writeString(javaFile.toPath(), javaCode);

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        // Pour une simple class, pas de smell
        assertTrue(smells.stream().noneMatch(s -> true), "No smells should be detected");
    }

    @Test
    void testDetectEmptyFile(@TempDir Path tempDir) throws IOException {
        File javaFile = tempDir.resolve("Empty.java").toFile();
        Files.writeString(javaFile.toPath(), "");

        List<SmellResult> smells = detector.detect(javaFile);

        assertNotNull(smells);
        assertTrue(smells.isEmpty());
    }
}

