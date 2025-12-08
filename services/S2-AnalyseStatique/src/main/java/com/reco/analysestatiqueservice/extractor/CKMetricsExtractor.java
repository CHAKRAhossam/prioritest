package com.reco.analysestatiqueservice.extractor;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.*;
import com.reco.analysestatiqueservice.model.ClassMetrics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Extractor for CK (Chidamber and Kemerer) metrics suite.
 * Calculates metrics such as WMC, DIT, NOC, CBO, RFC, and LCOM.
 *
 * @author Reco Team
 */
@Component
public class CKMetricsExtractor {

    private static final Logger logger = LoggerFactory.getLogger(CKMetricsExtractor.class);

    /**
     * Extracts CK metrics for a Java class file.
     * Uses JavaParser for AST analysis and falls back to simple parsing if AST parsing fails.
     *
     * @param file The Java file to analyze
     * @return ClassMetrics object containing all extracted metrics
     * @throws IOException if file reading fails
     */
    public ClassMetrics extract(File file) throws IOException {
        logger.debug("Extracting CK metrics from: {}", file.getName());

        ClassMetrics m = new ClassMetrics();
        m.setClassName(file.getName().replace(".java", ""));
        m.setFilePath(file.getAbsolutePath());

        String code = Files.readString(file.toPath());

        try {
            CompilationUnit cu = StaticJavaParser.parse(code);

            // Get the first class or interface declaration
            Optional<ClassOrInterfaceDeclaration> classOpt =
                    cu.findFirst(ClassOrInterfaceDeclaration.class);

            // Calculate LOC (Lines of Code) for the entire file
            int loc = computeLoc(code);
            m.setLoc(loc);

            if (classOpt.isEmpty()) {
                // No class found, return minimal metrics
                logger.debug("No class declaration found in file: {}", file.getName());
                m.setMethodsCount(0);
                m.setAttributesCount(0);
                m.setWmc(0);
                m.setDit(0);
                m.setNoc(0);
                m.setCbo(0);
                m.setRfc(0);
                m.setLcom(0.0);
                return m;
            }

            ClassOrInterfaceDeclaration clazz = classOpt.get();

            // Count methods and attributes
            List<MethodDeclaration> methods = clazz.getMethods();
            List<ConstructorDeclaration> ctors = clazz.getConstructors();
            List<FieldDeclaration> fields = clazz.getFields();

            int methodCount = methods.size() + ctors.size();
            int attributeCount = fields.stream()
                    .mapToInt(f -> f.getVariables().size())
                    .sum();

            m.setMethodsCount(methodCount);
            m.setAttributesCount(attributeCount);

            // Calculate WMC (Weighted Methods per Class) - McCabe complexity
            int wmc = 0;
            for (MethodDeclaration md : methods) {
                wmc += computeCyclomatic(md);
            }
            for (ConstructorDeclaration cd : ctors) {
                wmc += computeCyclomatic(cd);
            }
            m.setWmc(wmc);

            // Calculate DIT (Depth of Inheritance Tree) - simplified version
            // Note: Full DIT requires global project analysis
            int dit = clazz.getExtendedTypes().isNonEmpty() ? 1 : 0;
            m.setDit(dit);

            // NOC (Number of Children) - requires global project view
            // Set to 0 as it cannot be calculated from a single file
            m.setNoc(0);

            // Calculate CBO (Coupling Between Objects)
            int cbo = computeCbo(clazz, cu);
            m.setCbo(cbo);

            // Calculate RFC (Response For Class)
            int rfc = computeRfc(clazz, methodCount);
            m.setRfc(rfc);

            // Calculate LCOM (Lack of Cohesion of Methods)
            double lcom = computeLcom(clazz);
            m.setLcom(lcom);

            logger.debug("Extracted metrics for {}: WMC={}, CBO={}, RFC={}, LCOM={}",
                    m.getClassName(), wmc, cbo, rfc, lcom);

            return m;

        } catch (Exception e) {
            // Fallback to simple parsing if AST parsing fails
            logger.warn("AST parsing failed for {}, using fallback method: {}", file.getName(), e.getMessage());
            return simpleFallback(file);
        }
    }

    // =======================
    // Helper Methods
    // =======================

    /**
     * Calculates Lines of Code (LOC) - non-empty, non-comment lines.
     *
     * @param code The source code as a string
     * @return Number of lines of code
     */
    private int computeLoc(String code) {
        String[] lines = code.split("\\R");
        int count = 0;
        for (String l : lines) {
            String trim = l.trim();
            if (trim.isEmpty()) continue;
            if (trim.startsWith("//")) continue;
            if (trim.startsWith("/*") || trim.startsWith("*")) continue;
            count++;
        }
        return count;
    }

    /**
     * Calculates cyclomatic complexity (McCabe) for a method or constructor.
     *
     * @param callable The method or constructor declaration
     * @return Cyclomatic complexity value
     */
    private int computeCyclomatic(CallableDeclaration<?> callable) {
        int c = 1; // base
        c += callable.findAll(IfStmt.class).size();
        c += callable.findAll(ForStmt.class).size();
        c += callable.findAll(ForEachStmt.class).size();
        c += callable.findAll(WhileStmt.class).size();
        c += callable.findAll(DoStmt.class).size();
        c += callable.findAll(SwitchEntry.class).size();
        c += callable.findAll(CatchClause.class).size();
        c += callable.findAll(ConditionalExpr.class).size();
        return c;
    }

    /**
     * Calculates CBO (Coupling Between Objects) - number of distinct external types used.
     *
     * @param clazz The class or interface declaration
     * @param cu    The compilation unit
     * @return CBO value
     */
    private int computeCbo(ClassOrInterfaceDeclaration clazz, CompilationUnit cu) {
        Set<String> types = new HashSet<>();

        // champs
        clazz.getFields().forEach(f ->
                types.add(f.getElementType().asString())
        );

        // méthodes : type de retour + paramètres
        clazz.getMethods().forEach(m -> {
            types.add(m.getType().asString());
            m.getParameters().forEach(p ->
                    types.add(p.getType().asString())
            );
        });

        // constructeurs : paramètres
        clazz.getConstructors().forEach(c ->
                c.getParameters().forEach(p ->
                        types.add(p.getType().asString())
                )
        );

        // variables locales
        cu.findAll(VariableDeclarator.class).forEach(v ->
                types.add(v.getType().asString())
        );

        // new Class(...)
        cu.findAll(ObjectCreationExpr.class).forEach(o ->
                types.add(o.getType().asString())
        );

        // imports
        cu.getImports().forEach(i ->
                types.add(i.getName().getIdentifier())
        );

        // clean : remove primitives, java.lang & self
        String selfName = clazz.getNameAsString();
        return (int) types.stream()
                .map(this::normalizeTypeName)
                .filter(t -> t != null && !t.isEmpty())
                .filter(t -> !isPrimitive(t))
                .filter(t -> !isJavaLang(t))
                .filter(t -> !t.equals(selfName))
                .distinct()
                .count();
    }

    private String normalizeTypeName(String t) {
        if (t == null) return null;
        // enlever generics: List<String> -> List
        int idx = t.indexOf('<');
        if (idx > 0) {
            t = t.substring(0, idx);
        }
        return t.trim();
    }

    private boolean isPrimitive(String t) {
        return Set.of(
                "byte","short","int","long","float","double","boolean","char",
                "Byte","Short","Integer","Long","Float","Double","Boolean","Character"
        ).contains(t);
    }

    private boolean isJavaLang(String t) {
        // simple check: types communs java.lang
        return Set.of(
                "String", "Object", "Throwable", "Exception", "RuntimeException"
        ).contains(t);
    }

    /**
     * Calculates RFC (Response For Class) - class methods plus called methods.
     *
     * @param clazz       The class or interface declaration
     * @param methodCount Number of methods in the class
     * @return RFC value
     */
    private int computeRfc(ClassOrInterfaceDeclaration clazz, int methodCount) {
        Set<String> called = new HashSet<>();
        clazz.findAll(MethodCallExpr.class).forEach(mc ->
                called.add(mc.getNameAsString())
        );
        return methodCount + called.size();
    }

    /**
     * Calculates LCOM (Lack of Cohesion of Methods) - measures method cohesion.
     *
     * @param clazz The class or interface declaration
     * @return LCOM value
     */
    private double computeLcom(ClassOrInterfaceDeclaration clazz) {
        List<MethodDeclaration> methods = clazz.getMethods();
        if (methods.size() < 2) return 0.0;

        // noms des champs
        Set<String> fieldNames = clazz.getFields().stream()
                .flatMap(f -> f.getVariables().stream())
                .map(v -> v.getNameAsString())
                .collect(Collectors.toSet());

        // pour chaque méthode : champs utilisés
        List<Set<String>> usage = new ArrayList<>();
        for (MethodDeclaration m : methods) {
            Set<String> used = new HashSet<>();
            m.findAll(NameExpr.class).forEach(ne -> {
                if (fieldNames.contains(ne.getNameAsString())) {
                    used.add(ne.getNameAsString());
                }
            });
            m.findAll(FieldAccessExpr.class).forEach(fe -> {
                if (fieldNames.contains(fe.getNameAsString())) {
                    used.add(fe.getNameAsString());
                }
            });
            usage.add(used);
        }

        int n = methods.size();
        int P = 0; // paires sans intersection
        int Q = 0; // paires avec intersection

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                Set<String> s1 = usage.get(i);
                Set<String> s2 = usage.get(j);

                Set<String> inter = new HashSet<>(s1);
                inter.retainAll(s2);

                if (inter.isEmpty()) {
                    P++;
                } else {
                    Q++;
                }
            }
        }

        if (P > Q) {
            return P - Q;
        } else {
            return 0.0;
        }
    }

    /**
     * Fallback method when JavaParser fails to parse the file.
     * Uses simple line-based parsing to extract basic metrics.
     *
     * @param file The Java file to analyze
     * @return ClassMetrics with basic metrics
     * @throws IOException if file reading fails
     */
    private ClassMetrics simpleFallback(File file) throws IOException {
        ClassMetrics m = new ClassMetrics();
        m.setClassName(file.getName().replace(".java", ""));
        m.setFilePath(file.getAbsolutePath());

        List<String> lines = Files.readAllLines(file.toPath());

        int loc = 0;
        int methods = 0;
        int attributes = 0;

        for (String line : lines) {
            String trimmed = line.trim();
            if (trimmed.isEmpty()) continue;
            if (trimmed.startsWith("//")) continue;
            if (trimmed.startsWith("/*") || trimmed.startsWith("*")) continue;

            loc++;

            if (trimmed.contains("(")
                    && trimmed.contains(")")
                    && trimmed.endsWith("{")) {
                methods++;
            } else if (trimmed.endsWith(";")
                    && !trimmed.contains("(")
                    && !trimmed.contains(")")) {
                attributes++;
            }
        }

        m.setLoc(loc);
        m.setMethodsCount(methods);
        m.setAttributesCount(attributes);

        // Set default values for metrics that cannot be calculated without AST
        m.setWmc(methods); // Approximate: assume complexity equals method count
        m.setDit(0);
        m.setNoc(0);
        m.setCbo(0);
        m.setRfc(0);
        m.setLcom(0.0);

        return m;
    }
}
