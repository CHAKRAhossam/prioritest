# 📋 Plan d'Implémentation - Persistance PostgreSQL/TimescaleDB

## 🎯 Objectif

Remplacer H2 en mémoire par PostgreSQL/TimescaleDB pour :
- ✅ Persister les métriques extraites
- ✅ Stocker l'historique par commit/classe
- ✅ Permettre l'analyse temporelle (TimescaleDB)
- ✅ Préparer l'intégration avec les autres microservices

---

## 📊 Architecture de la Base de Données

### Schéma Relationnel

```
┌─────────────┐
│   Project   │
├─────────────┤
│ id (PK)     │
│ name        │
│ repoUrl     │
│ createdAt   │
└─────────────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│  ClassMetrics    │
├──────────────────┤
│ id (PK)          │
│ projectId (FK)   │
│ className        │
│ filePath         │
│ commitHash       │
│ timestamp        │
│ loc              │
│ wmc              │
│ dit              │
│ noc              │
│ cbo              │
│ rfc              │
│ lcom             │
└──────────────────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│ DependencyEdge   │
├──────────────────┤
│ id (PK)          │
│ projectId (FK)   │
│ fromClass        │
│ toClass          │
│ commitHash       │
│ timestamp        │
└──────────────────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│   SmellResult    │
├──────────────────┤
│ id (PK)          │
│ projectId (FK)   │
│ className        │
│ smellType        │
│ line             │
│ commitHash       │
│ timestamp        │
└──────────────────┘
```

---

## 🔧 Étapes d'Implémentation

### **Étape 1 : Configuration PostgreSQL** (15 min)

#### 1.1 Ajouter dépendance PostgreSQL dans `pom.xml`
```xml
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

#### 1.2 Ajouter dépendance TimescaleDB (extension PostgreSQL)
- TimescaleDB est une extension PostgreSQL, pas besoin de dépendance Java supplémentaire
- Configuration via SQL après création de la base

#### 1.3 Configuration dans `application.properties`
```properties
# PostgreSQL Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/analyse_statique
spring.datasource.username=postgres
spring.datasource.password=postgres
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA/Hibernate Configuration
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.properties.hibernate.format_sql=true

# TimescaleDB (optionnel pour l'instant)
# On activera les hypertables plus tard si nécessaire
```

#### 1.4 Créer profil de développement (H2) et production (PostgreSQL)
- `application-dev.properties` : H2 pour tests rapides
- `application-prod.properties` : PostgreSQL pour production

---

### **Étape 2 : Créer les Entités JPA** (1h)

#### 2.1 Entité `Project`
```java
@Entity
@Table(name = "projects")
public class Project {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String name;
    
    private String repositoryUrl;
    
    @Column(nullable = false)
    private LocalDateTime createdAt;
    
    // Getters/Setters
}
```

#### 2.2 Entité `ClassMetricsEntity`
```java
@Entity
@Table(name = "class_metrics")
public class ClassMetricsEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;
    
    @Column(nullable = false)
    private String className;
    
    private String filePath;
    private String commitHash;
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    // Métriques CK
    private Integer loc;
    private Integer wmc;
    private Integer dit;
    private Integer noc;
    private Integer cbo;
    private Integer rfc;
    private Double lcom;
    
    // Getters/Setters
}
```

#### 2.3 Entité `DependencyEdgeEntity`
```java
@Entity
@Table(name = "dependency_edges")
public class DependencyEdgeEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;
    
    @Column(nullable = false)
    private String fromClass;
    
    @Column(nullable = false)
    private String toClass;
    
    private String commitHash;
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    // Getters/Setters
}
```

#### 2.4 Entité `SmellResultEntity`
```java
@Entity
@Table(name = "smell_results")
public class SmellResultEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;
    
    @Column(nullable = false)
    private String className;
    
    @Column(nullable = false)
    private String smellType;
    
    private Integer line;
    
    private String commitHash;
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    // Getters/Setters
}
```

---

### **Étape 3 : Créer les Repositories Spring Data** (30 min)

#### 3.1 `ProjectRepository`
```java
@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {
    Optional<Project> findByName(String name);
    Optional<Project> findByRepositoryUrl(String repositoryUrl);
}
```

#### 3.2 `ClassMetricsRepository`
```java
@Repository
public interface ClassMetricsRepository extends JpaRepository<ClassMetricsEntity, Long> {
    List<ClassMetricsEntity> findByProjectId(Long projectId);
    List<ClassMetricsEntity> findByProjectIdAndCommitHash(Long projectId, String commitHash);
    List<ClassMetricsEntity> findByProjectIdOrderByTimestampDesc(Long projectId);
    
    // Pour TimescaleDB - requêtes temporelles
    @Query("SELECT cm FROM ClassMetricsEntity cm WHERE cm.project.id = :projectId " +
           "AND cm.timestamp >= :startTime AND cm.timestamp <= :endTime")
    List<ClassMetricsEntity> findByProjectIdAndTimeRange(
        @Param("projectId") Long projectId,
        @Param("startTime") LocalDateTime startTime,
        @Param("endTime") LocalDateTime endTime
    );
}
```

#### 3.3 `DependencyEdgeRepository`
```java
@Repository
public interface DependencyEdgeRepository extends JpaRepository<DependencyEdgeEntity, Long> {
    List<DependencyEdgeEntity> findByProjectId(Long projectId);
    List<DependencyEdgeEntity> findByProjectIdAndCommitHash(Long projectId, String commitHash);
    List<DependencyEdgeEntity> findByFromClass(String fromClass);
    List<DependencyEdgeEntity> findByToClass(String toClass);
}
```

#### 3.4 `SmellResultRepository`
```java
@Repository
public interface SmellResultRepository extends JpaRepository<SmellResultEntity, Long> {
    List<SmellResultEntity> findByProjectId(Long projectId);
    List<SmellResultEntity> findByProjectIdAndCommitHash(Long projectId, String commitHash);
    List<SmellResultEntity> findByProjectIdAndSmellType(Long projectId, String smellType);
}
```

---

### **Étape 4 : Modifier MetricsService pour Persister** (1h)

#### 4.1 Ajouter injection des repositories
```java
@Service
public class MetricsService {
    private final ProjectRepository projectRepository;
    private final ClassMetricsRepository classMetricsRepository;
    private final DependencyEdgeRepository dependencyEdgeRepository;
    private final SmellResultRepository smellResultRepository;
    
    // Constructor injection
}
```

#### 4.2 Modifier `analyzeProject()` pour :
1. Créer ou récupérer le `Project`
2. Sauvegarder chaque `ClassMetrics` comme `ClassMetricsEntity`
3. Sauvegarder chaque `DependencyEdge` comme `DependencyEdgeEntity`
4. Sauvegarder chaque `SmellResult` comme `SmellResultEntity`
5. Utiliser `@Transactional` pour garantir la cohérence

#### 4.3 Gérer le commitHash
- Pour l'instant : générer un hash basé sur le contenu du ZIP
- Plus tard : recevoir le commitHash depuis le microservice CollecteDepots

---

### **Étape 5 : Migrations avec Flyway** (1h)

#### 5.1 Ajouter dépendance Flyway
```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

#### 5.2 Créer migrations SQL
- `V1__Create_projects_table.sql`
- `V2__Create_class_metrics_table.sql`
- `V3__Create_dependency_edges_table.sql`
- `V4__Create_smell_results_table.sql`
- `V5__Add_indexes.sql` (pour performance)
- `V6__Create_timescaledb_hypertables.sql` (optionnel)

#### 5.3 Configuration Flyway
```properties
spring.flyway.enabled=true
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-on-migrate=true
```

---

### **Étape 6 : Configuration TimescaleDB** (30 min - Optionnel)

#### 6.1 Créer hypertables pour séries temporelles
```sql
-- Convertir class_metrics en hypertable
SELECT create_hypertable('class_metrics', 'timestamp');

-- Convertir dependency_edges en hypertable
SELECT create_hypertable('dependency_edges', 'timestamp');

-- Convertir smell_results en hypertable
SELECT create_hypertable('smell_results', 'timestamp');
```

#### 6.2 Créer vues continues (continuous aggregates) pour analyses
```sql
-- Vue agrégée par jour
CREATE MATERIALIZED VIEW class_metrics_daily
WITH (timescaledb.continuous) AS
SELECT 
    project_id,
    time_bucket('1 day', timestamp) AS day,
    AVG(loc) AS avg_loc,
    AVG(wmc) AS avg_wmc,
    COUNT(*) AS class_count
FROM class_metrics
GROUP BY project_id, day;
```

---

### **Étape 7 : Tests** (1h)

#### 7.1 Tests unitaires des repositories
- Tester CRUD operations
- Tester requêtes personnalisées

#### 7.2 Tests d'intégration
- Tester persistance complète d'un projet
- Tester récupération des métriques
- Tester requêtes temporelles

#### 7.3 Configuration test avec H2
- Garder H2 pour tests rapides
- Utiliser `@TestPropertySource` pour override config

---

## 📁 Structure des Fichiers à Créer

```
analyse-statique-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/reco/analysestatiqueservice/
│   │   │       ├── entity/
│   │   │       │   ├── Project.java
│   │   │       │   ├── ClassMetricsEntity.java
│   │   │       │   ├── DependencyEdgeEntity.java
│   │   │       │   └── SmellResultEntity.java
│   │   │       ├── repository/
│   │   │       │   ├── ProjectRepository.java
│   │   │       │   ├── ClassMetricsRepository.java
│   │   │       │   ├── DependencyEdgeRepository.java
│   │   │       │   └── SmellResultRepository.java
│   │   │       └── service/
│   │   │           └── MetricsService.java (modifié)
│   │   └── resources/
│   │       ├── application.properties (modifié)
│   │       ├── application-dev.properties (nouveau)
│   │       ├── application-prod.properties (nouveau)
│   │       └── db/
│   │           └── migration/
│   │               ├── V1__Create_projects_table.sql
│   │               ├── V2__Create_class_metrics_table.sql
│   │               ├── V3__Create_dependency_edges_table.sql
│   │               ├── V4__Create_smell_results_table.sql
│   │               └── V5__Add_indexes.sql
│   └── test/
│       └── java/
│           └── .../repository/
│               ├── ProjectRepositoryTest.java
│               ├── ClassMetricsRepositoryTest.java
│               └── ...
└── pom.xml (modifié)
```

---

## ⏱️ Estimation du Temps

- **Étape 1** : Configuration PostgreSQL - 15 min
- **Étape 2** : Créer entités JPA - 1h
- **Étape 3** : Créer repositories - 30 min
- **Étape 4** : Modifier MetricsService - 1h
- **Étape 5** : Migrations Flyway - 1h
- **Étape 6** : TimescaleDB (optionnel) - 30 min
- **Étape 7** : Tests - 1h

**Total : ~5 heures** (sans TimescaleDB) ou **~5h30** (avec TimescaleDB)

---

## 🚀 Ordre d'Implémentation Recommandé

1. ✅ **Étape 1** : Configuration PostgreSQL (base)
2. ✅ **Étape 2** : Créer entités JPA (structure)
3. ✅ **Étape 3** : Créer repositories (accès données)
4. ✅ **Étape 4** : Modifier MetricsService (logique métier)
5. ✅ **Étape 5** : Migrations Flyway (versioning)
6. ✅ **Étape 7** : Tests (validation)
7. ⚠️ **Étape 6** : TimescaleDB (optimisation, optionnel)

---

## 📝 Notes Importantes

1. **CommitHash** : Pour l'instant, on génère un hash du ZIP. Plus tard, il viendra du microservice CollecteDepots.

2. **Transaction** : Utiliser `@Transactional` sur `analyzeProject()` pour garantir que toutes les métriques sont sauvegardées ensemble.

3. **Performance** : Ajouter des index sur :
   - `project_id`
   - `commit_hash`
   - `timestamp` (pour TimescaleDB)
   - `className` (pour recherches)

4. **Migration H2 → PostgreSQL** : 
   - Garder H2 pour tests
   - Utiliser profils Spring pour dev/prod

5. **TimescaleDB** : 
   - Nécessite PostgreSQL avec extension TimescaleDB installée
   - Très utile pour analyses temporelles
   - Peut être ajouté plus tard si nécessaire

---

## ✅ Critères de Succès

- [ ] PostgreSQL configuré et connecté
- [ ] Toutes les entités JPA créées
- [ ] Tous les repositories fonctionnels
- [ ] MetricsService persiste les données
- [ ] Migrations Flyway appliquées
- [ ] Tests passent
- [ ] Données persistées après redémarrage
- [ ] Requêtes temporelles fonctionnent (si TimescaleDB)

---

**Prêt à commencer ?** 🚀



