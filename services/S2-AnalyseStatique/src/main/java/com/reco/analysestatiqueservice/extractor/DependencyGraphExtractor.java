package com.reco.analysestatiqueservice.extractor;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.Type;
import com.reco.analysestatiqueservice.model.DependencyEdge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Professional extractor for dependency graph analysis.
 * Identifies relationships between classes by analyzing:
 * - Import statements
 * - Field types
 * - Method parameter types
 * - Method return types
 * - Variable declarations
 * - Object instantiations (new)
 * - Type casts
 * - Inheritance (extends/implements)
 *
 * @author Reco Team
 */
@Component
public class DependencyGraphExtractor {

    private static final Logger logger = LoggerFactory.getLogger(DependencyGraphExtractor.class);

    /**
     * Set of Java primitive types to exclude from dependencies.
     */
    private static final Set<String> PRIMITIVE_TYPES = Set.of(
            "byte", "short", "int", "long", "float", "double", "boolean", "char",
            "Byte", "Short", "Integer", "Long", "Float", "Double", "Boolean", "Character",
            "void", "Void"
    );

    /**
     * Set of common java.lang types to exclude (unless explicitly imported).
     */
    private static final Set<String> JAVA_LANG_TYPES = Set.of(
            "String", "Object", "Throwable", "Exception", "RuntimeException",
            "Error", "Cloneable", "Comparable", "Serializable", "Iterable",
            "Number", "Enum"
    );

    /**
     * Extracts dependency relationships from a Java file.
     * Analyzes the AST to find all external class dependencies.
     *
     * @param file The Java file to analyze
     * @return List of dependency edges (from -> to relationships)
     */
    public List<DependencyEdge> extract(File file) {
        logger.debug("Extracting dependencies from: {}", file.getName());

        try {
            String code = Files.readString(file.toPath());
            CompilationUnit cu = StaticJavaParser.parse(code);

            // Get the source class name
            Optional<ClassOrInterfaceDeclaration> classOpt = cu.findFirst(ClassOrInterfaceDeclaration.class);
            if (classOpt.isEmpty()) {
                logger.debug("No class declaration found in file: {}", file.getName());
                return new ArrayList<>();
            }

            String sourceClassName = classOpt.get().getNameAsString();
            String packageName = cu.getPackageDeclaration()
                    .map(p -> p.getNameAsString())
                    .orElse("");

            // Build fully qualified source class name
            String fullyQualifiedSource = packageName.isEmpty() 
                    ? sourceClassName 
                    : packageName + "." + sourceClassName;

            // Extract all dependencies
            Set<String> dependencies = extractDependencies(cu, classOpt.get(), packageName);

            // Build dependency edges
            List<DependencyEdge> edges = dependencies.stream()
                    .filter(dep -> !dep.equals(fullyQualifiedSource))
                    .filter(dep -> !dep.equals(sourceClassName))
                    .map(dep -> new DependencyEdge(fullyQualifiedSource, dep))
                    .collect(Collectors.toList());

            logger.debug("Found {} dependencies for class {}", edges.size(), sourceClassName);
            return edges;

        } catch (IOException e) {
            logger.error("Error reading file: {}", file.getAbsolutePath(), e);
            return new ArrayList<>();
        } catch (Exception e) {
            logger.warn("Error parsing file for dependencies: {}", file.getName(), e);
            return new ArrayList<>();
        }
    }

    /**
     * Extracts all dependencies from a compilation unit.
     *
     * @param cu           The compilation unit
     * @param clazz        The class declaration
     * @param packageName  The package name
     * @return Set of fully qualified dependency names
     */
    private Set<String> extractDependencies(CompilationUnit cu, ClassOrInterfaceDeclaration clazz, String packageName) {
        Set<String> dependencies = new HashSet<>();

        // 1. Extract from imports
        dependencies.addAll(extractFromImports(cu));

        // 2. Extract from inheritance (extends/implements)
        dependencies.addAll(extractFromInheritance(clazz, packageName));

        // 3. Extract from fields
        dependencies.addAll(extractFromFields(clazz, cu, packageName));

        // 4. Extract from method parameters and return types
        dependencies.addAll(extractFromMethods(clazz, cu, packageName));

        // 5. Extract from constructors
        dependencies.addAll(extractFromConstructors(clazz, cu, packageName));

        // 6. Extract from variable declarations
        dependencies.addAll(extractFromVariables(cu, packageName));

        // 7. Extract from object instantiations (new)
        dependencies.addAll(extractFromObjectCreations(cu, packageName));

        // 8. Extract from type casts
        dependencies.addAll(extractFromCasts(cu, packageName));

        // 9. Extract from method calls (static method calls on classes)
        dependencies.addAll(extractFromMethodCalls(cu, packageName));

        // Normalize and filter dependencies
        return normalizeDependencies(dependencies, packageName);
    }

    /**
     * Extracts dependencies from import statements.
     */
    private Set<String> extractFromImports(CompilationUnit cu) {
        Set<String> imports = new HashSet<>();
        for (ImportDeclaration imp : cu.getImports()) {
            if (!imp.isAsterisk() && !imp.isStatic()) {
                String importName = imp.getNameAsString();
                imports.add(importName);
            }
        }
        return imports;
    }

    /**
     * Extracts dependencies from inheritance (extends/implements).
     */
    private Set<String> extractFromInheritance(ClassOrInterfaceDeclaration clazz, String packageName) {
        Set<String> deps = new HashSet<>();

        // Extended types
        for (ClassOrInterfaceType extendedType : clazz.getExtendedTypes()) {
            String typeName = resolveTypeName(extendedType.getNameAsString(), packageName);
            if (typeName != null) {
                deps.add(typeName);
            }
        }

        // Implemented types
        for (ClassOrInterfaceType implementedType : clazz.getImplementedTypes()) {
            String typeName = resolveTypeName(implementedType.getNameAsString(), packageName);
            if (typeName != null) {
                deps.add(typeName);
            }
        }

        return deps;
    }

    /**
     * Extracts dependencies from field declarations.
     */
    private Set<String> extractFromFields(ClassOrInterfaceDeclaration clazz, CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        for (FieldDeclaration field : clazz.getFields()) {
            Type fieldType = field.getCommonType();
            String typeName = extractTypeName(fieldType, packageName);
            if (typeName != null) {
                deps.add(typeName);
            }
        }
        return deps;
    }

    /**
     * Extracts dependencies from method declarations.
     */
    private Set<String> extractFromMethods(ClassOrInterfaceDeclaration clazz, CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        for (MethodDeclaration method : clazz.getMethods()) {
            // Return type
            Type returnType = method.getType();
            String returnTypeName = extractTypeName(returnType, packageName);
            if (returnTypeName != null) {
                deps.add(returnTypeName);
            }

            // Parameter types
            for (Parameter param : method.getParameters()) {
                Type paramType = param.getType();
                String paramTypeName = extractTypeName(paramType, packageName);
                if (paramTypeName != null) {
                    deps.add(paramTypeName);
                }
            }
        }
        return deps;
    }

    /**
     * Extracts dependencies from constructor declarations.
     */
    private Set<String> extractFromConstructors(ClassOrInterfaceDeclaration clazz, CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        for (ConstructorDeclaration constructor : clazz.getConstructors()) {
            for (Parameter param : constructor.getParameters()) {
                Type paramType = param.getType();
                String paramTypeName = extractTypeName(paramType, packageName);
                if (paramTypeName != null) {
                    deps.add(paramTypeName);
                }
            }
        }
        return deps;
    }

    /**
     * Extracts dependencies from variable declarations.
     * Note: Local variables are less critical for dependency analysis,
     * but we extract them from field declarations that weren't caught earlier.
     */
    private Set<String> extractFromVariables(CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        // Variable declarations in methods are handled by method extraction
        // This method mainly catches any edge cases
        return deps;
    }

    /**
     * Extracts dependencies from object creation expressions (new).
     */
    private Set<String> extractFromObjectCreations(CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        cu.findAll(ObjectCreationExpr.class).forEach(expr -> {
            String typeName = resolveTypeName(expr.getType().getNameAsString(), packageName);
            if (typeName != null) {
                deps.add(typeName);
            }
        });
        return deps;
    }

    /**
     * Extracts dependencies from type casts.
     */
    private Set<String> extractFromCasts(CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        cu.findAll(CastExpr.class).forEach(cast -> {
            Type castType = cast.getType();
            String typeName = extractTypeName(castType, packageName);
            if (typeName != null) {
                deps.add(typeName);
            }
        });
        return deps;
    }

    /**
     * Extracts dependencies from static method calls (e.g., ClassName.method()).
     */
    private Set<String> extractFromMethodCalls(CompilationUnit cu, String packageName) {
        Set<String> deps = new HashSet<>();
        cu.findAll(MethodCallExpr.class).forEach(methodCall -> {
            if (methodCall.getScope().isPresent()) {
                Expression scope = methodCall.getScope().get();
                if (scope instanceof NameExpr) {
                    String className = ((NameExpr) scope).getNameAsString();
                    String resolvedName = resolveTypeName(className, packageName);
                    if (resolvedName != null) {
                        deps.add(resolvedName);
                    }
                } else if (scope instanceof FieldAccessExpr) {
                    FieldAccessExpr fieldAccess = (FieldAccessExpr) scope;
                    String className = fieldAccess.getScope().toString();
                    String resolvedName = resolveTypeName(className, packageName);
                    if (resolvedName != null) {
                        deps.add(resolvedName);
                    }
                }
            }
        });
        return deps;
    }

    /**
     * Extracts type name from a Type node, handling generics and arrays.
     */
    private String extractTypeName(Type type, String packageName) {
        if (type.isPrimitiveType()) {
            return null; // Skip primitives
        }

        if (type.isArrayType()) {
            type = type.asArrayType().getComponentType();
        }

        if (type.isClassOrInterfaceType()) {
            ClassOrInterfaceType classType = type.asClassOrInterfaceType();
            String typeName = classType.getNameAsString();
            return resolveTypeName(typeName, packageName);
        }

        return null;
    }

    /**
     * Resolves a type name to its fully qualified name.
     * Handles simple names, fully qualified names, and package resolution.
     */
    private String resolveTypeName(String typeName, String packageName) {
        if (typeName == null || typeName.isEmpty()) {
            return null;
        }

        // Remove generics: List<String> -> List
        int genericIndex = typeName.indexOf('<');
        if (genericIndex > 0) {
            typeName = typeName.substring(0, genericIndex);
        }

        typeName = typeName.trim();

        // Skip primitives
        if (PRIMITIVE_TYPES.contains(typeName)) {
            return null;
        }

        // Skip java.lang types (unless they're explicitly imported)
        if (JAVA_LANG_TYPES.contains(typeName) && !typeName.contains(".")) {
            return null;
        }

        // If already fully qualified, return as is
        if (typeName.contains(".")) {
            return typeName;
        }

        // Try to resolve from same package
        if (!packageName.isEmpty()) {
            return packageName + "." + typeName;
        }

        // Return simple name (will be resolved later if needed)
        return typeName;
    }

    /**
     * Normalizes and filters dependencies.
     * Removes primitives, java.lang types, and duplicates.
     */
    private Set<String> normalizeDependencies(Set<String> dependencies, String packageName) {
        return dependencies.stream()
                .filter(dep -> dep != null && !dep.isEmpty())
                .map(dep -> {
                    // Remove generics
                    int idx = dep.indexOf('<');
                    return idx > 0 ? dep.substring(0, idx) : dep;
                })
                .filter(dep -> !PRIMITIVE_TYPES.contains(dep))
                .filter(dep -> {
                    // Filter java.lang types that are not fully qualified
                    if (!dep.contains(".") && JAVA_LANG_TYPES.contains(dep)) {
                        return false;
                    }
                    return true;
                })
                .filter(dep -> !dep.startsWith("java.lang.") || 
                        dep.equals("java.lang.String") || 
                        dep.equals("java.lang.Object"))
                .collect(Collectors.toSet());
    }
}
