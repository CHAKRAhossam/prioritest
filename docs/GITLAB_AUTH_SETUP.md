# Configuration de l'Authentification GitLab (SSO/SAML)

## Problème Identifié

Votre compte GitLab utilise l'authentification SSO/SAML, ce qui empêche l'utilisation d'un mot de passe pour HTTPS. Vous devez utiliser un **Personal Access Token** (PAT).

## Solution : Créer un Personal Access Token

### Étape 1 : Créer le Token

1. Allez sur votre profil GitLab : https://gitlab.com/-/user_settings/personal_access_tokens
   - Ou : Cliquez sur votre avatar (en haut à droite) → **Preferences** → **Access Tokens**

2. Créez un nouveau token :
   - **Token name** : `prioritest-dev` (ou un nom de votre choix)
   - **Expiration date** : Choisissez une date (ou laissez vide pour pas d'expiration)
   - **Select scopes** : Cochez au minimum :
     - ✅ `write_repository` (pour push/pull)
     - ✅ `read_repository` (pour clone/fetch)
     - ✅ `api` (optionnel, pour l'API)

3. Cliquez sur **Create personal access token**

4. **⚠️ IMPORTANT** : Copiez le token immédiatement ! Il ne sera affiché qu'une seule fois.
   - Le token ressemble à : `glpat-xxxxxxxxxxxxxxxxxxxx`

### Étape 2 : Configurer Git pour utiliser le Token

#### Option A : Utiliser le token dans l'URL (Recommandé)

```bash
# Remplacer USERNAME par votre username GitLab
# Remplacer TOKEN par le token que vous venez de créer
git remote set-url origin https://USERNAME:TOKEN@gitlab.com/chakrahossam-group/prioritest.git
```

Exemple :
```bash
git remote set-url origin https://chakrahossam:glpat-xxxxxxxxxxxxxxxxxxxx@gitlab.com/chakrahossam-group/prioritest.git
```

#### Option B : Utiliser Git Credential Manager (Windows)

1. Quand Git vous demande les credentials :
   - **Username** : Votre username GitLab
   - **Password** : Collez votre Personal Access Token (pas votre mot de passe)

2. Windows sauvegardera automatiquement les credentials.

#### Option C : Utiliser SSH (Alternative)

Si vous préférez SSH :

1. **Générer une clé SSH** :
   ```bash
   ssh-keygen -t ed25519 -C "hchakra8@gmail.com"
   ```

2. **Copier la clé publique** :
   ```powershell
   # PowerShell
   Get-Content C:\Users\$env:USERNAME\.ssh\id_ed25519.pub
   ```

3. **Ajouter la clé sur GitLab** :
   - Allez sur : https://gitlab.com/-/profile/keys
   - Collez la clé publique
   - Cliquez sur **Add key**

4. **Changer le remote vers SSH** :
   ```bash
   git remote set-url origin git@gitlab.com:chakrahossam-group/prioritest.git
   ```

### Étape 3 : Tester la Connexion

```bash
# Tester avec fetch
git fetch origin

# Ou tester avec push
git push origin main
```

## Sécurité

⚠️ **Ne partagez jamais votre Personal Access Token !**

- Ne le commitez pas dans le code
- Ne le partagez pas publiquement
- Si le token est compromis, révoquez-le immédiatement et créez-en un nouveau

## Révoquer un Token

Si vous devez révoquer un token :

1. Allez sur : https://gitlab.com/-/user_settings/personal_access_tokens
2. Cliquez sur **Revoke** à côté du token concerné

## Vérification

Après configuration, vous devriez pouvoir :

```bash
# Pousser vers GitLab
git push origin main

# Et cela poussera automatiquement vers GitHub aussi (grâce à la config des deux pushurl)
```

## Aide Supplémentaire

- Documentation GitLab : https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
- Guide SSH : https://docs.gitlab.com/ee/user/ssh.html

