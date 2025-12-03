# Utiliser votre Personal Access Token avec Git Credential Manager

## Token Créé ✅

Votre token : `glpat-DL3nJkGiW7jBF3Ije4CoEm86MQp1Oml5ZmpnCw.01.121jfd8hs`

## Configuration Git Credential Manager

### Étape 1 : Activer Git Credential Manager

```bash
git config --global credential.helper manager-core
```

✅ Cette commande est déjà exécutée.

### Étape 2 : Premier Push (Git vous demandera les credentials)

Quand vous ferez votre premier `git push origin main`, Git vous demandera :

1. **Username** : Entrez votre **username GitLab** (pas votre email)
   - Pour trouver votre username : https://gitlab.com/-/profile
   - C'est généralement `chakrahossam` ou similaire

2. **Password** : Collez votre **Personal Access Token**
   - `glpat-DL3nJkGiW7jBF3Ije4CoEm86MQp1Oml5ZmpnCw.01.121jfd8hs`
   - ⚠️ **Ne mettez PAS votre mot de passe GitLab**, utilisez le token !

3. Windows sauvegardera automatiquement ces credentials dans le Credential Manager.

### Étape 3 : Tester Maintenant

Essayons de pousser maintenant. Git vous demandera les credentials :

```bash
git push origin main
```

**Quand Git vous demande les credentials :**
- **Username** : Votre username GitLab
- **Password** : `glpat-DL3nJkGiW7jBF3Ije4CoEm86MQp1Oml5ZmpnCw.01.121jfd8hs`

## Alternative : Utiliser le Token Directement dans l'URL

Si vous préférez ne pas être demandé à chaque fois, vous pouvez mettre le token dans l'URL :

```bash
# Remplacer USERNAME par votre username GitLab
git remote set-url origin https://USERNAME:glpat-DL3nJkGiW7jBF3Ije4CoEm86MQp1Oml5ZmpnCw.01.121jfd8hs@gitlab.com/chakrahossam-group/prioritest.git
```

⚠️ **Note** : Cette méthode stocke le token dans `.git/config`. C'est pratique mais moins sécurisé si vous partagez le repo.

## Vérifier les Credentials Sauvegardés

Pour voir les credentials sauvegardés dans Windows :

1. Ouvrez **Paramètres Windows** → **Comptes** → **Gestionnaire d'informations d'identification**
2. Ou tapez `credential` dans le menu Démarrer
3. Cherchez `git:https://gitlab.com` dans la liste

## Problèmes Courants

### "Authentication failed"

- Vérifiez que vous utilisez le **token** et non votre mot de passe
- Vérifiez que le token n'a pas expiré
- Vérifiez que le token a les scopes `write_repository` et `read_repository`

### "Username not found"

- Utilisez votre **username GitLab**, pas votre email
- Trouvez-le sur : https://gitlab.com/-/profile

### Effacer les Credentials Sauvegardés

Si vous devez réessayer :

```bash
# Effacer les credentials GitLab
git credential-manager-core erase
# Puis entrez :
# protocol=https
# host=gitlab.com
# (Laissez username et password vides, puis appuyez deux fois sur Entrée)
```

Ou via Windows :
1. **Paramètres** → **Comptes** → **Gestionnaire d'informations d'identification**
2. Cherchez `git:https://gitlab.com`
3. Cliquez sur **Modifier** ou **Supprimer**

