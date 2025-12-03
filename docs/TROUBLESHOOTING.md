# Guide de Dépannage - Connexion GitLab

## Problème : Impossible de se connecter à GitLab (port 443)

### Solutions possibles

#### 1. Utiliser SSH au lieu de HTTPS

Si HTTPS ne fonctionne pas, configurez SSH :

```bash
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "votre.email@example.com"

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub
# (Sur Windows: type C:\Users\VotreNom\.ssh\id_ed25519.pub)

# Ajouter la clé sur GitLab :
# 1. Allez sur https://gitlab.com/-/profile/keys
# 2. Collez votre clé publique
# 3. Sauvegardez

# Changer le remote vers SSH
git remote set-url origin git@gitlab.com:chakrahossam-group/prioritest.git
```

#### 2. Vérifier le proxy/firewall

Si vous êtes derrière un proxy d'entreprise :

```bash
# Configurer le proxy Git
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy https://proxy.example.com:8080

# Ou désactiver le proxy si non nécessaire
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 3. Utiliser GitHub en attendant

Le repository est aussi disponible sur GitHub :

```bash
# Pousser vers GitHub
git push github main
```

#### 4. Vérifier les credentials Git

```bash
# Windows : Vérifier le credential manager
git config --global credential.helper manager-core

# Réessayer avec authentification
git push origin main
```

#### 5. Désactiver temporairement SSL (non recommandé, seulement pour test)

```bash
git config --global http.sslVerify false
# ⚠️ Réactiver après : git config --global http.sslVerify true
```

### Alternative : Utiliser l'interface web GitLab

Si Git ne fonctionne pas, vous pouvez :
1. Aller sur https://gitlab.com/chakrahossam-group/prioritest
2. Uploader les fichiers via l'interface web
3. Ou utiliser GitLab Desktop : https://about.gitlab.com/install/#gitlab-desktop

### Contact

Si le problème persiste, contactez l'admin du projet.

