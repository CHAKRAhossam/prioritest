# Guide de Démarrage Rapide pour l'Équipe

## 📋 Checklist Avant de Commencer

- [ ] Créer un compte GitLab : https://gitlab.com/users/sign_up
- [ ] Vérifier votre email GitLab
- [ ] Accepter l'invitation au projet (vérifiez vos emails)
- [ ] Installer Git sur votre machine
- [ ] Configurer Git (nom et email)

## 🚀 Étapes Rapides

### 1. Créer un Compte GitLab

Si vous n'avez pas encore de compte :

1. Allez sur : https://gitlab.com/users/sign_up
2. Créez un compte avec votre email de l'équipe
3. Vérifiez votre email
4. Informez l'admin (Hossam Chakra) que votre compte est prêt

### 2. Accepter l'Invitation

1. Vérifiez vos emails pour l'invitation GitLab
2. Cliquez sur "Accept invitation"
3. Vous aurez maintenant accès au projet

### 3. Cloner le Repository

```bash
git clone https://gitlab.com/chakrahossam-group/prioritest.git
cd prioritest
```

### 4. Configurer l'Authentification

Si votre compte utilise SSO/SAML, créez un Personal Access Token :

📖 **Voir le guide** : `docs/GITLAB_AUTH.md`

### 5. Créer Votre Branche

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

### 6. Commencer le Développement

Chaque membre travaille dans son dossier de service :

```bash
# Exemple pour Haytam (Service 1)
cd services/S1-CollecteDepots
# Créer la structure de base
mkdir -p src tests
touch src/main.py requirements.txt Dockerfile
```

## 📚 Documentation Complète

- `docs/SETUP_TEAM.md` : Guide complet d'onboarding
- `docs/GITLAB_AUTH.md` : Guide d'authentification GitLab
- `STRUCTURE_PROJET.md` : Structure détaillée du projet

## ❓ Besoin d'Aide ?

Contactez l'admin du projet : Hossam Chakra (hchakra8@gmail.com)

