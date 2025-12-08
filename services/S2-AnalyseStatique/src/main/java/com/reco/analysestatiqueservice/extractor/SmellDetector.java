package com.reco.analysestatiqueservice.extractor;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.reco.analysestatiqueservice.model.SmellResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Professional detector for code smells in Java files.
 * Detects common code smells:
 * - God Class: Class with too many responsibilities (high LOC, WMC, CBO)
 * - Long Method: Method with too many lines of code
 * - Feature Envy: Method that uses more data from other classes than its own
 * - Data Class: Class with only getters/setters and no business logic
 * - Long Parameter List: Method with too many parameters
 * - Primitive Obsession: Excessive use of primitive types
 *
 * @author Reco Team
 */
@Component
public class SmellDetector {

    private static final Logger logger = LoggerFactory.getLogger(SmellDetector.class);

    // Thresholds for smell detection (configurable)
    @Value("${smell.godclass.loc:500}")
    public int godClassLocThreshold;
    @Value("${smell.godclass.wmc:50}")
    public int godClassWmcThreshold;
    @Value("${smell.godclass.cbo:10}")
    public int godClassCboThreshold;
    @Value("${smell.longmethod.loc:50}")
    public int longMethodLocThreshold;
    @Value("${smell.longparameterlist.count:5}")
    public int longParameterListThreshold;
    @Value("${smell.dataclass.method:10}")
    public int dataClassMethodThreshold;
    @Value("${smell.featureenvy.ratio:0.5}")
    public double featureEnvyRatioThreshold;

    /**
     * Detects code smells in a Java file.
     * Requires ClassMetrics to be calculated first for accurate detection.
     *
     * @param file The Java file to analyze
     * @return List of detected code smells
     */
    public List<SmellResult> detect(File file) {
        logger.debug("Detecting smells in: {}", file.getName());

        try {
            String code = Files.readString(file.toPath());
            CompilationUnit cu = StaticJavaParser.parse(code);

            Optional<ClassOrInterfaceDeclaration> classOpt = cu.findFirst(ClassOrInterfaceDeclaration.class);
            if (classOpt.isEmpty()) {
                return new ArrayList<>();
            }

            ClassOrInterfaceDeclaration clazz = classOpt.get();
            String className = clazz.getNameAsString();
            List<SmellResult> smells = new ArrayList<>();

            // Calculate basic metrics for smell detection
            int classLoc = calculateClassLoc(clazz, code);
            int wmc = calculateWmc(clazz);
            int cbo = estimateCbo(clazz, cu);
            int methodCount = clazz.getMethods().size() + clazz.getConstructors().size();

            // 1. Detect God Class
            if (isGodClass(classLoc, wmc, cbo)) {
                String details = String.format("LOC=%d, WMC=%d, CBO=%d (seuils LOC=%d, WMC=%d, CBO=%d)", classLoc, wmc, cbo, godClassLocThreshold, godClassWmcThreshold, godClassCboThreshold);
                smells.add(new SmellResult("God Class", className, clazz.getBegin().map(p -> p.line).orElse(1), details));
                logger.debug("Detected God Class: {} (LOC={}, WMC={}, CBO={})", className, classLoc, wmc, cbo);
            }

            // 2. Detect Long Methods
            smells.addAll(detectLongMethods(clazz, className));

            // 3. Detect Long Parameter Lists
            smells.addAll(detectLongParameterLists(clazz, className));

            // 4. Detect Data Class
            if (isDataClass(clazz, methodCount)) {
                String details = String.format("Getter/Setters: %d (seuil methodes=%d)", methodCount, dataClassMethodThreshold);
                smells.add(new SmellResult("Data Class", className, clazz.getBegin().map(p -> p.line).orElse(1), details));
                logger.debug("Detected Data Class: {}", className);
            }

            // 5. Detect Feature Envy (simplified)
            smells.addAll(detectFeatureEnvy(clazz, className, cu));

            logger.debug("Found {} smells in class {}", smells.size(), className);
            return smells;

        } catch (IOException e) {
            logger.error("Error reading file: {}", file.getAbsolutePath(), e);
            return new ArrayList<>();
        } catch (Exception e) {
            logger.warn("Error detecting smells in file: {}", file.getName(), e);
            return new ArrayList<>();
        }
    }

    /**
     * Detects if a class is a God Class (too many responsibilities).
     */
    private boolean isGodClass(int loc, int wmc, int cbo) {
        return loc > godClassLocThreshold 
                && wmc > godClassWmcThreshold 
                && cbo > godClassCboThreshold;
    }

    /**
     * Detects Long Methods (methods with too many lines).
     */
    private List<SmellResult> detectLongMethods(ClassOrInterfaceDeclaration clazz, String className) {
        List<SmellResult> smells = new ArrayList<>();

        for (MethodDeclaration method : clazz.getMethods()) {
            int methodLoc = calculateMethodLoc(method);
            if (methodLoc > longMethodLocThreshold) {
                int line = method.getBegin().map(p -> p.line).orElse(1);
                String details = String.format("LOC=%d (seuil=%d)", methodLoc, longMethodLocThreshold);
                smells.add(new SmellResult("Long Method", className, line, details));
                logger.debug("Detected Long Method: {}.{} (LOC={})", className, method.getNameAsString(), methodLoc);
            }
        }

        return smells;
    }

    /**
     * Detects methods with too many parameters.
     */
    private List<SmellResult> detectLongParameterLists(ClassOrInterfaceDeclaration clazz, String className) {
        List<SmellResult> smells = new ArrayList<>();

        for (MethodDeclaration method : clazz.getMethods()) {
            int paramCount = method.getParameters().size();
            if (paramCount > longParameterListThreshold) {
                int line = method.getBegin().map(p -> p.line).orElse(1);
                String details = String.format("Params=%d (seuil=%d)", paramCount, longParameterListThreshold);
                smells.add(new SmellResult("Long Parameter List", className, line, details));
                logger.debug("Detected Long Parameter List: {}.{} ({} parameters)", className, method.getNameAsString(), paramCount);
            }
        }

        for (ConstructorDeclaration constructor : clazz.getConstructors()) {
            int paramCount = constructor.getParameters().size();
            if (paramCount > longParameterListThreshold) {
                int line = constructor.getBegin().map(p -> p.line).orElse(1);
                smells.add(new SmellResult("Long Parameter List", className, line));
                logger.debug("Detected Long Parameter List: {}.<init> ({} parameters)", className, paramCount);
            }
        }

        return smells;
    }

    /**
     * Detects if a class is a Data Class (only getters/setters, no business logic).
     */
    private boolean isDataClass(ClassOrInterfaceDeclaration clazz, int methodCount) {
        if (methodCount == 0) {
            return false; // No methods at all
        }

        if (methodCount > dataClassMethodThreshold) {
            return false; // Too many methods, probably has business logic
        }

        // Check if all methods are getters/setters
        boolean allGettersSetters = true;
        for (MethodDeclaration method : clazz.getMethods()) {
            String methodName = method.getNameAsString();
            if (!isGetterOrSetter(methodName, method)) {
                allGettersSetters = false;
                break;
            }
        }

        return allGettersSetters && methodCount > 0;
    }

    /**
     * Checks if a method is a getter or setter.
     */
    private boolean isGetterOrSetter(String methodName, MethodDeclaration method) {
        // Getter: starts with "get" or "is", no parameters, returns non-void
        if ((methodName.startsWith("get") || methodName.startsWith("is")) 
                && method.getParameters().isEmpty()
                && !method.getType().isVoidType()) {
            return true;
        }

        // Setter: starts with "set", one parameter, returns void
        if (methodName.startsWith("set") 
                && method.getParameters().size() == 1
                && method.getType().isVoidType()) {
            return true;
        }

        return false;
    }

    /**
     * Detects Feature Envy (method uses more data from other classes).
     * Simplified version: detects methods with many external method calls.
     */
    private List<SmellResult> detectFeatureEnvy(ClassOrInterfaceDeclaration clazz, 
                                                 String className, 
                                                 CompilationUnit cu) {
        List<SmellResult> smells = new ArrayList<>();

        for (MethodDeclaration method : clazz.getMethods()) {
            // Count external method calls (calls on other objects)
            long externalCalls = method.findAll(MethodCallExpr.class).stream()
                    .filter(mc -> {
                        // If scope is present and not "this", it's an external call
                        return mc.getScope().isPresent() 
                                && !mc.getScope().get().toString().equals("this");
                    })
                    .count();

            // Count internal method calls (calls on "this" or no scope)
            long internalCalls = method.findAll(MethodCallExpr.class).stream()
                    .filter(mc -> {
                        return !mc.getScope().isPresent() 
                                || mc.getScope().get().toString().equals("this");
                    })
                    .count();

            // If external calls significantly outnumber internal calls, it's Feature Envy
            long totalCalls = externalCalls + internalCalls;
            if (totalCalls > 0) {
                double externalRatio = (double) externalCalls / totalCalls;
                if (externalRatio > featureEnvyRatioThreshold && externalCalls > 3) {
                    int line = method.getBegin().map(p -> p.line).orElse(1);
                    smells.add(new SmellResult("Feature Envy", className, line, String.format("external_ratio=%.2f (seuil=%.2f), externalCalls=%d", externalRatio, featureEnvyRatioThreshold, externalCalls)));
                    logger.debug("Detected Feature Envy: {}.{} (external ratio: {})", 
                            className, method.getNameAsString(), externalRatio);
                }
            }
        }

        return smells;
    }

    /**
     * Calculates Lines of Code for a class.
     */
    private int calculateClassLoc(ClassOrInterfaceDeclaration clazz, String code) {
        if (!clazz.getBegin().isPresent() || !clazz.getEnd().isPresent()) {
            return 0;
        }

        int startLine = clazz.getBegin().get().line;
        int endLine = clazz.getEnd().get().line;
        return endLine - startLine + 1;
    }

    /**
     * Calculates WMC (Weighted Methods per Class) - cyclomatic complexity.
     */
    private int calculateWmc(ClassOrInterfaceDeclaration clazz) {
        int wmc = 0;
        for (MethodDeclaration method : clazz.getMethods()) {
            wmc += calculateMethodComplexity(method);
        }
        for (ConstructorDeclaration constructor : clazz.getConstructors()) {
            wmc += calculateMethodComplexity(constructor);
        }
        return wmc;
    }

    /**
     * Calculates cyclomatic complexity for a method/constructor.
     */
    private int calculateMethodComplexity(CallableDeclaration<?> callable) {
        int complexity = 1; // Base complexity
        complexity += callable.findAll(com.github.javaparser.ast.stmt.IfStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.ForStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.ForEachStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.WhileStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.DoStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.SwitchStmt.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.stmt.CatchClause.class).size();
        complexity += callable.findAll(com.github.javaparser.ast.expr.ConditionalExpr.class).size();
        return complexity;
    }

    /**
     * Estimates CBO (Coupling Between Objects) for smell detection.
     */
    private int estimateCbo(ClassOrInterfaceDeclaration clazz, CompilationUnit cu) {
        // Simplified CBO calculation
        java.util.Set<String> types = new java.util.HashSet<>();

        // Fields
        clazz.getFields().forEach(f -> types.add(f.getElementType().asString()));

        // Method parameters and return types
        clazz.getMethods().forEach(m -> {
            types.add(m.getType().asString());
            m.getParameters().forEach(p -> types.add(p.getType().asString()));
        });

        // Object creations
        cu.findAll(com.github.javaparser.ast.expr.ObjectCreationExpr.class)
                .forEach(o -> types.add(o.getType().getNameAsString()));

        // Filter primitives and java.lang
        return (int) types.stream()
                .filter(t -> t != null && !t.isEmpty())
                .filter(t -> !isPrimitiveType(t))
                .filter(t -> !t.startsWith("java.lang.") || t.equals("java.lang.String"))
                .distinct()
                .count();
    }

    /**
     * Calculates Lines of Code for a method.
     */
    private int calculateMethodLoc(MethodDeclaration method) {
        if (!method.getBegin().isPresent() || !method.getEnd().isPresent()) {
            return 0;
        }
        int startLine = method.getBegin().get().line;
        int endLine = method.getEnd().get().line;
        return endLine - startLine + 1;
    }

    /**
     * Checks if a type is a primitive.
     */
    private boolean isPrimitiveType(String type) {
        return java.util.Set.of("byte", "short", "int", "long", "float", "double", "boolean", "char",
                "Byte", "Short", "Integer", "Long", "Float", "Double", "Boolean", "Character",
                "void", "Void").contains(type);
    }
}
