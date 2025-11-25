# Service 4 - Prétraitement des Features

**Responsable :** Hicham Kaou  
**Email :** kaouhicham@gmail.com

## Description

Nettoyage, imputation, encodage ; construction de features dérivées (churn, nb auteurs, fréquence modifs, proximité avec bug-fix commits).

## Technologies

- Pandas, scikit-learn
- SMOTE pour balancement
- DVC pour data lineage
- Feast (feature store)

## User Stories

- US-S4-01: Pipeline de nettoyage
- US-S4-02: Features dérivées - Churn
- US-S4-03: Features dérivées - Auteurs
- US-S4-04: Features dérivées - Bug-fix proximity
- US-S4-05: Split temporel train/val/test
- US-S4-06: Balancement de classes
- US-S4-07: Data lineage avec DVC
- US-S4-08: Feature Store Feast

