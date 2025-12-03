# Ajouter les Credentials GitLab Manuellement dans Windows

## Méthode 1 : Via l'Interface Graphique Windows (Recommandé)

### Étapes

1. **Ouvrir le Gestionnaire d'informations d'identification Windows** :
   - Appuyez sur `Windows + R`
   - Tapez : `control /name Microsoft.CredentialManager`
   - Appuyez sur `Entrée`
   
   **OU**
   
   - Allez dans **Paramètres Windows** → **Comptes** → **Gestionnaire d'informations d'identification**
   - Ou cherchez "Credential Manager" dans le menu Démarrer

2. **Cliquez sur "Informations d'identification Windows"** (en haut)

3. **Cliquez sur "Ajouter une information d'identification"** (ou "Add a credential")

4. **Remplissez les champs** :
   - **Adresse Internet ou réseau** : `git:https://gitlab.com`
   - **Nom d'utilisateur** : Votre **username GitLab** (pas votre email)
     - Pour trouver votre username : https://gitlab.com/-/profile
     - C'est généralement `chakrahossam` ou similaire
   - **Mot de passe** : Votre **Personal Access Token GitLab**
     - ⚠️ **Ne mettez PAS votre mot de passe GitLab**, utilisez le token !
     - Le token ressemble à : `glpat-xxxxxxxxxxxxxxxxxxxx`

5. **Cliquez sur "OK"**

6. **Testez** :
   ```bash
   git push origin main
   ```

## Méthode 2 : Via PowerShell (Avancé)

Si vous préférez la ligne de commande :

```powershell
# Installer le module CredentialManager (une seule fois)
Install-Module -Name CredentialManager -Force

# Ajouter les credentials
$cred = Get-Credential -UserName "VOTRE_USERNAME_GITLAB" -Message "Entrez votre token GitLab"
$cred | Add-StoredCredential -Target "git:https://gitlab.com"
```

Quand PowerShell vous demande le mot de passe, collez votre **Personal Access Token**.

## Méthode 3 : Via Git (Automatique)

La méthode la plus simple est de laisser Git le faire automatiquement :

1. **Assurez-vous que Git Credential Manager est configuré** :
   ```bash
   git config --global credential.helper manager
   ```

2. **Essayez de pousser** :
   ```bash
   git push origin main
   ```

3. **Git vous demandera les credentials** :
   - **Username** : Votre username GitLab
   - **Password** : Votre Personal Access Token

4. **Windows sauvegardera automatiquement** les credentials.

## Vérifier les Credentials Sauvegardés

Pour voir si les credentials sont bien sauvegardés :

1. Ouvrez le **Gestionnaire d'informations d'identification**
2. Cherchez `git:https://gitlab.com`
3. Vous devriez voir votre username

## Modifier ou Supprimer les Credentials

1. Ouvrez le **Gestionnaire d'informations d'identification**
2. Cherchez `git:https://gitlab.com`
3. Cliquez sur la flèche pour développer
4. Cliquez sur **Modifier** ou **Supprimer**

## Important

- **Username** : Utilisez votre **username GitLab**, pas votre email
- **Password** : Utilisez votre **Personal Access Token**, pas votre mot de passe GitLab
- Le token ressemble à : `glpat-xxxxxxxxxxxxxxxxxxxx`

## Trouver Votre Username GitLab

1. Allez sur : https://gitlab.com/-/profile
2. Votre username est affiché en haut de la page
3. C'est généralement différent de votre email

## Exemple

Si votre username GitLab est `chakrahossam` et votre token est `glpat-ABC123XYZ` :

- **Adresse Internet** : `git:https://gitlab.com`
- **Nom d'utilisateur** : `chakrahossam`
- **Mot de passe** : `glpat-ABC123XYZ`

