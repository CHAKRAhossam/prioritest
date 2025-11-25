# Configuration des Remotes Git

## Remotes configurés

Le projet est configuré pour pousser vers **deux repositories** simultanément :

1. **GitLab** (équipe) : https://gitlab.com/chakrahossam-group/prioritest
2. **GitHub** (personnel) : https://github.com/CHAKRAhossam/prioritest

## Configuration actuelle

```bash
# Voir les remotes
git remote -v
```

Le remote `origin` est configuré pour pousser vers les deux repos en même temps.

## Utilisation

### Pousser vers les deux repos

```bash
git push origin main
```

Cette commande poussera automatiquement vers GitLab ET GitHub.

### Pousser vers un seul repo

```bash
# Seulement GitLab
git push gitlab main

# Seulement GitHub
git push github main
```

## Vérification

Pour vérifier que les deux repos sont à jour :

- GitLab : https://gitlab.com/chakrahossam-group/prioritest
- GitHub : https://github.com/CHAKRAhossam/prioritest

