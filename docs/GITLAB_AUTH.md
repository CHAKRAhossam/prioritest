# Authentification GitLab pour l'Équipe

## Problème : Compte SSO/SAML

Si votre compte GitLab utilise SSO/SAML, vous ne pouvez pas utiliser un mot de passe pour HTTPS. Vous devez créer un **Personal Access Token**.

## Solution : Créer un Personal Access Token

### Étapes

1. Allez sur : https://gitlab.com/-/user_settings/personal_access_tokens
   - Ou : Votre profil → **Preferences** → **Access Tokens**

2. Créez un nouveau token :
   - **Token name** : `prioritest-dev`
   - **Expiration date** : (optionnel)
   - **Select scopes** : Cochez au minimum :
     - ✅ `write_repository`
     - ✅ `read_repository`

3. Cliquez sur **Create personal access token**

4. **⚠️ IMPORTANT** : Copiez le token immédiatement ! Il ne sera affiché qu'une seule fois.

### Utiliser le Token

Quand Git vous demande les credentials lors d'un `git push` ou `git pull` :

- **Username** : Votre username GitLab (pas votre email)
- **Password** : Collez votre **Personal Access Token** (pas votre mot de passe GitLab)

Windows sauvegardera automatiquement ces credentials.

### Alternative : SSH

Si vous préférez SSH :

1. Générez une clé SSH : `ssh-keygen -t ed25519 -C "votre.email@example.com"`
2. Ajoutez la clé sur GitLab : https://gitlab.com/-/profile/keys
3. Changez le remote : `git remote set-url origin git@gitlab.com:chakrahossam-group/prioritest.git`

## Aide

- Documentation GitLab : https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
- Guide SSH : https://docs.gitlab.com/ee/user/ssh.html

