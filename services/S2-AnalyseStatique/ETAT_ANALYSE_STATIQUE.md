# 📊 État d'Avancement - Microservice AnalyseStatique

## 🎯 Vue d'Ensemble

**Microservice** : AnalyseStatique  
**Progression** : ~50%  
**Statut** : ⚠️ Partiellement fonctionnel  
**Application** : ✅ Démarrée et opérationnelle sur port 8080

---

## ✅ CE QUI EST FAIT (50%)

### 1. **Architecture & Infrastructure** ✅
- ✅ Application Spring Boot 3.5.8 fonctionnelle
- ✅ API REST opérationnelle
- ✅ Structure modulaire (Controller → Service → Extractors)
- ✅ Code professionnel (logging, DI, exception handling)
- ✅ Tests unitaires de base

### 2. **Extraction ZIP** ✅
- ✅ `ZipExtractor` : Extraction de projets ZIP
- ✅ Filtrage des dossiers inutiles (target, .git, .idea, etc.)
- ✅ Protection contre Zip Slip Attack
- ✅ Nettoyage automatique des fichiers temporaires

### 3. **Découverte de Fichiers Java** ✅
- ✅ `JavaParserExtractor` : Scan récursif des fichiers .java
- ✅ Détection automatique de tous les fichiers Java dans un projet
- ✅ Retourne liste détaillée avec chemins

### 4. **Métriques CK Implémentées** ✅

#### ✅ LOC (Lines of Code)
- Calcul des lignes de code (non-vides, non-commentaires)
- Fonctionne correctement

#### ✅ WMC (Weighted Methods per Class)
- Complexité cyclomatique de McCabe
- Calcul par méthode (if, for, while, switch, catch, etc.)
- Somme pour toute la classe
- **Implémentation complète et correcte**

#### ✅ DIT (Depth of Inheritance Tree)
- Version simplifiée : détecte si la classe extends une autre classe
- ⚠️ **Limitation** : Ne calcule pas la profondeur réelle (nécessite vue globale du projet)
- Retourne 0 ou 1 actuellement

#### ✅ CBO (Coupling Between Objects)
- Détection des types utilisés (champs, paramètres, retours, imports)
- Filtrage des primitives et types Java.lang
- Compte les dépendances externes
- **Implémentation approximative mais fonctionnelle**

#### ✅ RFC (Response For Class)
- Nombre de méthodes de la classe + méthodes appelées
- **Implémentation correcte**

#### ✅ LCOM (Lack of Cohesion of Methods)
- Calcul basé sur l'utilisation des champs par les méthodes
- Formule : P - Q (paires de méthodes sans intersection - avec intersection)
- **Implémentation correcte**

### 5. **Outils Utilisés** ✅
- ✅ JavaParser 3.25.8 pour analyse AST
- ✅ Bibliothèque CK 0.6.0 (dépendance présente)
- ✅ Fallback en cas d'échec de parsing

### 6. **API REST** ✅
- ✅ Endpoint : `POST /metrics/analyze`
- ✅ Accepte : `MultipartFile` (ZIP)
- ✅ Retourne : `MetricsResponse` (JSON)
- ✅ Gestion d'erreurs centralisée (`GlobalExceptionHandler`)
- ✅ Validation des entrées

### 7. **Qualité du Code** ✅
- ✅ Logging SLF4J complet
- ✅ Injection de dépendances Spring
- ✅ Gestion d'exceptions professionnelle
- ✅ JavaDoc complète
- ✅ Commentaires en anglais
- ✅ Tests unitaires (CKMetricsExtractor, JavaParserExtractor, MetricsService)

---

## ⚠️ CE QUI EST PARTIELLEMENT FAIT (25%)

### 1. **Extraction des Dépendances** ⚠️
- ✅ Structure de classe `DependencyGraphExtractor` présente
- ✅ Modèle `DependencyEdge` défini
- ❌ **Implémentation vide** : retourne toujours liste vide
- ❌ Pas de calcul des dépendances in/out degree
- ❌ Pas de graphe de dépendances

**Ce qui manque** :
- Analyse des imports
- Analyse des types utilisés dans les méthodes
- Construction du graphe de dépendances
- Calcul du in-degree (combien de classes dépendent de cette classe)
- Calcul du out-degree (combien de classes cette classe utilise)

### 2. **Détection de Smells** ⚠️
- ✅ Structure de classe `SmellDetector` présente
- ✅ Modèle `SmellResult` défini
- ❌ **Implémentation vide** : retourne toujours liste vide
- ❌ Aucun smell détecté

**Ce qui manque** :
- Détection "God Class" (classe trop grande, trop de responsabilités)
- Détection "Long Method" (méthode trop longue)
- Détection "Feature Envy" (méthode utilise plus les données d'autres classes)
- Détection "Data Class" (classe avec seulement getters/setters)
- Détection "Primitive Obsession" (usage excessif de primitives)
- Détection "Duplicate Code"

---

## ❌ CE QUI MANQUE (25%)

### 1. **Métriques Manquantes** ❌

#### ❌ NOC (Number of Children)
- **Problème** : Nécessite une vue globale du projet
- **Actuellement** : Retourne toujours 0
- **Solution** : Analyser toutes les classes du projet pour trouver les sous-classes

#### ❌ DIT Complet
- **Problème** : Version simplifiée (0 ou 1)
- **Solution** : Calculer la profondeur réelle de l'arbre d'héritage

#### ❌ Métriques de Dépendances
- In-degree : nombre de classes qui dépendent de cette classe
- Out-degree : nombre de classes que cette classe utilise
- **Solution** : Implémenter `DependencyGraphExtractor`

### 2. **Base de Données** ❌
- ❌ Utilise H2 en mémoire (données perdues au redémarrage)
- ❌ Pas de PostgreSQL/TimescaleDB
- ❌ Pas de persistance des métriques
- ❌ Pas de stockage par commit/classe
- ❌ Pas de versioning des métriques

**Ce qui manque** :
- Configuration PostgreSQL
- Entités JPA pour stocker les métriques
- Repositories Spring Data
- Tables pour : classes, métriques, commits, projets

### 3. **Feature Store (Feast)** ❌
- ❌ Pas d'intégration Feast
- ❌ Pas de versioning des features
- ❌ Pas de réutilisation online/offline

### 4. **Normalisation & Multi-Projets** ❌
- ❌ Pas de normalisation par module/langage
- ❌ Pas de gestion multi-projets
- ❌ Pas de support multi-langages (seulement Java)

### 5. **Intégrations** ❌
- ❌ Pas d'API gRPC (seulement REST)
- ❌ Pas d'intégration Kafka
- ❌ Pas de webhooks

### 6. **Optimisations** ❌
- ❌ Pas de cache
- ❌ Pas de traitement asynchrone pour gros projets
- ❌ Pas de parallélisation de l'analyse

---

## 📋 Plan d'Action pour Compléter (Priorités)

### 🔴 **Priorité HAUTE** (2-3 semaines)

#### 1. Implémenter Extraction Dépendances
- [ ] Analyser imports dans chaque fichier
- [ ] Extraire types utilisés (champs, paramètres, retours)
- [ ] Construire graphe de dépendances
- [ ] Calculer in-degree et out-degree
- [ ] Retourner liste de `DependencyEdge`

**Fichiers à modifier** :
- `DependencyGraphExtractor.java` (implémentation complète)

#### 2. Implémenter Détection Smells
- [ ] Détecter "God Class" (LOC > seuil, WMC > seuil, CBO > seuil)
- [ ] Détecter "Long Method" (LOC méthode > seuil)
- [ ] Détecter "Feature Envy" (analyse des appels externes)
- [ ] Détecter "Data Class" (seulement getters/setters)
- [ ] Retourner liste de `SmellResult` avec type et ligne

**Fichiers à modifier** :
- `SmellDetector.java` (implémentation complète)

#### 3. Calculer NOC (Number of Children)
- [ ] Analyser toutes les classes du projet
- [ ] Construire arbre d'héritage
- [ ] Compter enfants pour chaque classe
- [ ] Mettre à jour `ClassMetrics.noc`

**Fichiers à modifier** :
- `CKMetricsExtractor.java` (ajouter analyse globale)
- `MetricsService.java` (passer en 2 passes : 1. toutes les classes, 2. calcul NOC)

### 🟡 **Priorité MOYENNE** (2-3 semaines)

#### 4. Ajouter PostgreSQL/TimescaleDB
- [ ] Configuration PostgreSQL dans `application.properties`
- [ ] Créer entités JPA :
  - `Project` (id, name, repositoryUrl, createdAt)
  - `ClassMetrics` (id, projectId, className, filePath, commitHash, timestamp, loc, wmc, dit, noc, cbo, rfc, lcom)
  - `DependencyEdge` (id, projectId, fromClass, toClass, commitHash, timestamp)
  - `SmellResult` (id, projectId, className, smellType, line, commitHash, timestamp)
- [ ] Créer repositories Spring Data
- [ ] Modifier `MetricsService` pour persister les métriques
- [ ] Créer migrations Liquibase/Flyway

**Fichiers à créer/modifier** :
- `application.properties` (configuration DB)
- `entity/Project.java`
- `entity/ClassMetricsEntity.java`
- `entity/DependencyEdgeEntity.java`
- `entity/SmellResultEntity.java`
- `repository/ClassMetricsRepository.java`
- `repository/DependencyEdgeRepository.java`
- `repository/SmellResultRepository.java`
- `pom.xml` (ajouter dépendances PostgreSQL, Liquibase)

#### 5. Calculer DIT Complet
- [ ] Analyser chaîne d'héritage complète
- [ ] Calculer profondeur réelle (1 = Object, 2 = extends Object, etc.)
- [ ] Mettre à jour `ClassMetrics.dit`

**Fichiers à modifier** :
- `CKMetricsExtractor.java` (améliorer calcul DIT)

### 🟢 **Priorité BASSE** (Optionnel)

#### 6. Feature Store (Feast)
- [ ] Intégrer Feast SDK
- [ ] Définir features dans Feast
- [ ] Exporter métriques vers Feast

#### 7. Support Multi-Langages
- [ ] Ajouter support Python (radon)
- [ ] Ajouter support autres langages

#### 8. API gRPC
- [ ] Définir protobuf
- [ ] Implémenter service gRPC

---

## 📊 Métriques de Progression

### Fonctionnalités
- ✅ Extraction ZIP : 100%
- ✅ Découverte fichiers : 100%
- ✅ Métriques CK de base : 85% (LOC, WMC, RFC, LCOM = 100%, DIT = 50%, CBO = 80%, NOC = 0%)
- ⚠️ Extraction dépendances : 10% (structure seulement)
- ⚠️ Détection smells : 10% (structure seulement)
- ❌ Persistance : 0%
- ❌ Feature Store : 0%

### Code Quality
- ✅ Architecture : 100%
- ✅ Logging : 100%
- ✅ Exception Handling : 100%
- ✅ Tests : 60% (tests de base, manque tests d'intégration)
- ✅ Documentation : 100%

### Infrastructure
- ❌ Base de données : 0% (H2 seulement)
- ❌ Feature Store : 0%
- ❌ Kafka : 0%
- ❌ gRPC : 0%

---

## 🎯 Objectif Final

**Microservice AnalyseStatique complet doit** :
1. ✅ Extraire toutes les métriques CK (LOC, WMC, DIT, NOC, CBO, RFC, LCOM)
2. ⚠️ Extraire graphe de dépendances avec in/out degree
3. ⚠️ Détecter code smells (God Class, Long Method, etc.)
4. ❌ Persister métriques dans PostgreSQL/TimescaleDB
5. ❌ Exporter vers Feast (optionnel)
6. ❌ Support multi-langages (optionnel)

**État actuel** : 50% - Base solide, métriques principales fonctionnelles, manque dépendances, smells et persistance.



