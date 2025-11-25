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
# Méthode 1 : Push automatique vers les deux
git push origin main

# Méthode 2 : Utiliser le script PowerShell (Windows)
.\push-all.ps1

# Méthode 3 : Utiliser le script Bash (Linux/Mac)
./push-all.sh
```

La commande `git push origin main` poussera automatiquement vers GitLab ET GitHub grâce à la configuration des deux `pushurl`.

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

