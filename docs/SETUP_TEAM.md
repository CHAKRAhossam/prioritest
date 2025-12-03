# Guide d'Onboarding pour l'Équipe

## 🔐 Accès au Repository

### GitLab (Repository Principal - Équipe)

Le repository principal est sur GitLab : https://gitlab.com/chakrahossam-group/prioritest

**Pour ajouter les membres de l'équipe :**

1. Allez sur https://gitlab.com/chakrahossam-group/prioritest
2. Cliquez sur **Settings** → **Members** (ou **Paramètres** → **Membres**)
3. Cliquez sur **Invite members**
4. Ajoutez les emails des membres de l'équipe :
   - `haytamnajam14@gmail.com` (Haytam Ta)
   - `kaouhicham@gmail.com` (Hicham Kaou)
   - `hchakra8@gmail.com` (Hossam Chakra)
   - `im.michich@gmail.com` (Ilyas Michich)
   - `oussamaboujdig8@gmail.com` (Oussama Boujdig)
5. Sélectionnez le rôle **Developer** ou **Maintainer**
6. Envoyez l'invitation

### Authentification GitLab

Si votre compte utilise SSO/SAML, vous devez créer un **Personal Access Token**.

📖 **Voir le guide** : `docs/GITLAB_AUTH.md`

## 🚀 Configuration Initiale pour les Membres

### 1. Cloner le Repository

```bash
# Cloner depuis GitLab
git clone https://gitlab.com/chakrahossam-group/prioritest.git
cd prioritest
```

### 2. Configurer Git (si pas déjà fait)

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

### 3. Créer une Branche pour Votre Service

Chaque membre doit créer sa propre branche pour travailler :

```bash
# Haytam Ta - Services 1 & 2
git checkout -b feature/haytam-s1-s2-collecte-analyse

# Hicham Kaou - Services 4 & 5
git checkout -b feature/hicham-s4-s5-pretraitement-ml

# Hossam Chakra - Services 6 & 7
git checkout -b feature/hossam-s6-s7-priorisation-scaffolder

# Ilyas Michich - Service 8
git checkout -b feature/ilyas-s8-dashboard

# Oussama Boujdig - Services 3 & 9
git checkout -b feature/oussama-s3-s9-historique-integrations
```

### 4. Installer les Dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 5. Démarrer le Développement

Chaque membre travaille dans son dossier de service :

```bash
# Exemple pour Haytam (Service 1)
cd services/S1-CollecteDepots
# Créer la structure de base
mkdir -p src tests
touch src/main.py requirements.txt Dockerfile
```

## 📋 Workflow de Collaboration

### 1. Travailler sur sa Branche

```bash
# Toujours partir de main à jour
git checkout main
git pull origin main

# Créer/switch vers votre branche
git checkout feature/votre-branche

# Faire vos modifications
# ...

# Commiter régulièrement
git add .
git commit -m "Description de vos changements"
```

### 2. Pousser sa Branche

```bash
# Pousser votre branche sur GitLab
git push origin feature/votre-branche
```

### 3. Créer une Merge Request

1. Allez sur GitLab : https://gitlab.com/chakrahossam-group/prioritest
2. Cliquez sur **Merge requests** → **New merge request**
3. Sélectionnez votre branche → `main`
4. Remplissez la description
5. Assignez un reviewer (un autre membre de l'équipe)
6. Créez la merge request

### 4. Code Review

- Les autres membres peuvent reviewer votre code
- Faire les corrections demandées
- Une fois approuvé, merge dans `main`

## 🎯 Assignation des Services

| Membre | Services | Branche Suggérée |
|--------|----------|------------------|
| **Haytam Ta** | S1-CollecteDepots<br>S2-AnalyseStatique | `feature/haytam-s1-s2` |
| **Hicham Kaou** | S4-PretraitementFeatures<br>S5-MLService | `feature/hicham-s4-s5` |
| **Hossam Chakra** | S6-MoteurPriorisation<br>S7-TestScaffolder | `feature/hossam-s6-s7` |
| **Ilyas Michich** | S8-DashboardQualite | `feature/ilyas-s8` |
| **Oussama Boujdig** | S3-HistoriqueTests<br>S9-Integrations | `feature/oussama-s3-s9` |

## 📚 Ressources

- **Jira** : https://prioritest.atlassian.net/browse/MTP
- **Board Scrum** : https://prioritest.atlassian.net/jira/software/projects/MTP/boards/134
- **Structure du Projet** : Voir `STRUCTURE_PROJET.md` à la racine

## ❓ Questions ?

En cas de problème :
1. Vérifier que vous avez bien accès au repository GitLab
2. Vérifier que votre branche est à jour avec `main`
3. Contacter l'admin du projet (Hossam Chakra)

