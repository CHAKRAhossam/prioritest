# Liste des Figures Requises pour le Rapport

Ce document liste toutes les figures qui doivent être ajoutées au rapport LaTeX.

## Structure des dossiers

```
docs/
├── diagrams/          # Diagrammes techniques
├── maquettes/        # Maquettes UI/UX Figma
└── logos/            # Logos (EMSI.png)
```

## Diagrammes Techniques (diagrams/)

### Architecture

- [x] `Architecture_Prioritest_General.drawio` - Architecture générale (existe déjà)
- [x] `Architecture_Prioritest_Complete.drawio` - Architecture complète (existe déjà)
- [ ] `flux_donnees.png` - Schéma des flux de données principaux (à créer)

### BPMN

- [ ] `bpmn_s1_collecte.svg` - Diagramme BPMN Service 1 (Collecte Depots)
- [ ] `bpmn_s2_analyse.svg` - Diagramme BPMN Service 2 (Analyse Statique)
- [ ] `bpmn_s3_historique.svg` - Diagramme BPMN Service 3 (Historique Tests)
- [ ] `bpmn_s4_pretraitement.svg` - Diagramme BPMN Service 4 (Pretraitement Features)
- [ ] `bpmn_s5_ml.svg` - Diagramme BPMN Service 5 (ML Service)
- [x] `service6_swimlanes.svg` - Diagramme BPMN Service 6 (existe déjà)
- [x] `diagramBPMN_S7.svg` - Diagramme BPMN Service 7 (existe déjà)
- [ ] `bpmn_s8_dashboard.svg` - Diagramme BPMN Service 8 (Dashboard Qualité)
- [ ] `bpmn_s9_integrations.svg` - Diagramme BPMN Service 9 (Integrations & Ops)

**Création :** Utiliser un outil BPMN (bpmn.io, Camunda Modeler, ou Draw.io avec templates BPMN) pour créer ces diagrammes avec swimlanes et descriptions détaillées des processus métiers.

### Diagrammes de Classes

- [ ] `class_diagram_s1.png` - Diagramme de classes Service 1 (Collecte Depots)
- [ ] `class_diagram_s2.png` - Diagramme de classes Service 2 (Analyse Statique)
- [ ] `class_diagram_s3.png` - Diagramme de classes Service 3 (Historique Tests)
- [ ] `class_diagram_s4.png` - Diagramme de classes Service 4 (Pretraitement Features)
- [ ] `class_diagram_s5.png` - Diagramme de classes Service 5 (ML Service)
- [ ] `class_diagram_s6.png` - Diagramme de classes Service 6 (Moteur Priorisation)
  - **Source :** `class_diagram_s6_s7.puml` (existe déjà, extraire partie S6)
- [ ] `class_diagram_s7.png` - Diagramme de classes Service 7 (Test Scaffolder)
  - **Source :** `class_diagram_s6_s7.puml` (existe déjà, extraire partie S7)
- [ ] `class_diagram_s8.png` - Diagramme de classes Service 8 (Dashboard Qualité)
- [ ] `class_diagram_s9.png` - Diagramme de classes Service 9 (Integrations & Ops)

**Génération :** Utiliser PlantUML, Draw.io ou un outil UML pour créer ces diagrammes

### Cas d'Utilisation

- [ ] `use_case_diagram_global.png` - Diagramme de cas d'utilisation - Vue d'ensemble
- [ ] `use_case_diagram_s1.png` - Diagramme de cas d'utilisation Service 1
- [ ] `use_case_diagram_s2.png` - Diagramme de cas d'utilisation Service 2
- [ ] `use_case_diagram_s3.png` - Diagramme de cas d'utilisation Service 3
- [ ] `use_case_diagram_s4.png` - Diagramme de cas d'utilisation Service 4
- [ ] `use_case_diagram_s5.png` - Diagramme de cas d'utilisation Service 5
- [ ] `use_case_diagram_s6.png` - Diagramme de cas d'utilisation Service 6
  - **Source :** `use_case_diagram_s6_s7.puml` (existe déjà, extraire partie S6)
- [ ] `use_case_diagram_s7.png` - Diagramme de cas d'utilisation Service 7
  - **Source :** `use_case_diagram_s6_s7.puml` (existe déjà, extraire partie S7)
- [ ] `use_case_diagram_s8.png` - Diagramme de cas d'utilisation Service 8
- [ ] `use_case_diagram_s9.png` - Diagramme de cas d'utilisation Service 9

**Génération :** Utiliser PlantUML pour convertir les fichiers .puml existants, ou créer de nouveaux diagrammes pour les services manquants

## Maquettes UI/UX (maquettes/)

Toutes les maquettes doivent être exportées depuis Figma au format PNG avec une résolution appropriée (300 DPI recommandé).

- [ ] `dashboard_home.png` - Page d'accueil - Vue d'ensemble du dashboard
- [ ] `priorisation_plan.png` - Interface de visualisation des plans de priorisation
- [ ] `class_details.png` - Page de détails d'une classe avec métriques
- [ ] `coverage_charts.png` - Graphiques de couverture de tests (ligne, branche)
- [ ] `metrics_reports.png` - Interface de métriques et export de rapports

## Logos (logos/)

- [ ] `EMSI.png` - Logo de l'école (à ajouter)

## Instructions de Génération

### Diagrammes PlantUML

Pour générer les diagrammes depuis les fichiers PlantUML :

```bash
cd docs/diagrams

# Installer PlantUML si nécessaire
# Java est requis : https://plantuml.com/starting

# Générer les diagrammes
plantuml -tpng class_diagram_s6_s7.puml
plantuml -tpng use_case_diagram_s6_s7.puml
```

### Diagrammes Draw.io

Les fichiers `.drawio` peuvent être :
1. Ouverts dans https://app.diagrams.net/
2. Exportés en PNG/PDF depuis l'interface
3. Ou convertis via ligne de commande si draw.io est installé

### Maquettes Figma

1. Ouvrir les maquettes dans Figma
2. Sélectionner chaque frame/page
3. Exporter en PNG (300 DPI recommandé)
4. Sauvegarder dans `docs/maquettes/`

## Vérification

Avant de compiler le rapport, vérifier que tous les fichiers listés ci-dessus existent dans les dossiers appropriés. Le rapport LaTeX utilisera ces chemins pour insérer les figures.

## Notes

- Les fichiers existants sont marqués avec [x]
- Les fichiers à créer sont marqués avec [ ]
- Les chemins dans le fichier `.tex` sont relatifs au dossier `docs/`
- Si vous modifiez les noms de fichiers, mettez à jour les chemins dans `RAPPORT_PRIORITEST.tex`

