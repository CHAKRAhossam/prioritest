# Comment Utiliser Votre Nouveau Token GitLab

## Option 1 : Git Credential Manager (Recommandé) ✅

C'est la méthode la plus simple et sécurisée. Git vous demandera les credentials une fois, puis les sauvegardera.

### Étapes

1. **Assurez-vous que Git Credential Manager est activé** :
   ```bash
   git config --global credential.helper manager
   ```

2. **Poussez vers GitLab** :
   ```bash
   git push origin main
   ```

3. **Quand Git vous demande les credentials** :
   - **Username** : Votre username GitLab (pas votre email)
     - Pour trouver votre username : https://gitlab.com/-/profile
     - C'est généralement `chakrahossam` ou similaire
   - **Password** : Collez votre **nouveau Personal Access Token**
     - ⚠️ **Ne mettez PAS votre mot de passe GitLab**, utilisez le token !

4. Windows sauvegardera automatiquement ces credentials dans le Credential Manager.

5. **Les prochaines fois**, Git utilisera automatiquement les credentials sauvegardés.

## Option 2 : Token dans l'URL (Moins Sécurisé)

Si vous préférez mettre le token directement dans l'URL :

```bash
# Remplacer USERNAME par votre username GitLab
# Remplacer NEW_TOKEN par votre nouveau token
git remote set-url origin https://USERNAME:NEW_TOKEN@gitlab.com/chakrahossam-group/prioritest.git
```

Exemple :
```bash
git remote set-url origin https://chakrahossam:glpat-VOTRE_NOUVEAU_TOKEN@gitlab.com/chakrahossam-group/prioritest.git
```

⚠️ **Note** : Cette méthode stocke le token dans `.git/config`. C'est pratique mais moins sécurisé si vous partagez le repo.

## Option 3 : SSH (Meilleure Option Long Terme) 🔐

Si vous préférez SSH (plus sécurisé et pas besoin de token) :

```bash
# 1. Générer une clé SSH (si pas déjà fait)
ssh-keygen -t ed25519 -C "hchakra8@gmail.com"

# 2. Copier la clé publique
# PowerShell:
Get-Content C:\Users\$env:USERNAME\.ssh\id_ed25519.pub

# 3. Ajouter la clé sur GitLab :
#    https://gitlab.com/-/profile/keys
#    Collez la clé publique et sauvegardez

# 4. Changer le remote vers SSH
git remote set-url origin git@gitlab.com:chakrahossam-group/prioritest.git

# 5. Tester
git push origin main
```

## Vérifier la Configuration

Pour voir votre remote actuel :
```bash
git remote -v
```

## Problèmes Courants

### "Authentication failed"
- Vérifiez que vous utilisez le **token** et non votre mot de passe
- Vérifiez que le token n'a pas expiré
- Vérifiez que le token a les scopes `write_repository` et `read_repository`

### "Username not found"
- Utilisez votre **username GitLab**, pas votre email
- Trouvez-le sur : https://gitlab.com/-/profile

### Effacer les Anciens Credentials

Si vous devez réessayer avec un nouveau token :

1. **Via Windows Credential Manager** :
   - Ouvrez **Paramètres Windows** → **Comptes** → **Gestionnaire d'informations d'identification**
   - Cherchez `git:https://gitlab.com`
   - Supprimez l'entrée

2. **Ou via Git** :
   ```bash
   git credential-manager erase
   # Puis entrez :
   # protocol=https
   # host=gitlab.com
   # (Laissez username et password vides, puis appuyez deux fois sur Entrée)
   ```

## Recommandation

**Utilisez l'Option 1 (Git Credential Manager)** - C'est la plus simple et sécurisée. Vous n'aurez qu'à entrer le token une fois.

