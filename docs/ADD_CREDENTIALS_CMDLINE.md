# Ajouter les Credentials GitLab via Ligne de Commande Windows

## Méthode : Utiliser `cmdkey` (Windows intégré)

### Ajouter les Credentials

```cmd
cmdkey /add:git:https://gitlab.com /user:VOTRE_USERNAME_GITLAB /pass:VOTRE_TOKEN_GITLAB
```

**Exemple** :
```cmd
cmdkey /add:git:https://gitlab.com /user:chakrahossam /pass:glpat-VOTRE_NOUVEAU_TOKEN
```

⚠️ **Attention** : Le token sera visible dans l'historique de commandes PowerShell. Utilisez plutôt la méthode graphique ou laissez Git le faire automatiquement.

### Vérifier les Credentials

```cmd
cmdkey /list
```

Cherchez `git:https://gitlab.com` dans la liste.

### Supprimer les Credentials

```cmd
cmdkey /delete:git:https://gitlab.com
```

### Modifier les Credentials

1. Supprimez l'ancien :
   ```cmd
   cmdkey /delete:git:https://gitlab.com
   ```

2. Ajoutez le nouveau :
   ```cmd
   cmdkey /add:git:https://gitlab.com /user:VOTRE_USERNAME /pass:VOTRE_TOKEN
   ```

## Méthode Recommandée : Interface Graphique

Pour plus de sécurité, utilisez plutôt l'interface graphique (voir `docs/ADD_CREDENTIALS_MANUAL.md`).

## Test

Après avoir ajouté les credentials :

```bash
git push origin main
```

Git devrait utiliser automatiquement les credentials sauvegardés.

