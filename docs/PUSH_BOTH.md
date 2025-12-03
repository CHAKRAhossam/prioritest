# Comment Pousser vers GitHub et GitLab Simultanément

## Configuration Actuelle

Votre repository est configuré pour pousser vers les deux remotes :

- **GitLab** : https://gitlab.com/chakrahossam-group/prioritest.git
- **GitHub** : https://github.com/CHAKRAhossam/prioritest.git

## Problème : GitLab HTTPS ne fonctionne pas

Si GitLab HTTPS échoue (erreur port 443), Git s'arrête et ne pousse pas vers GitHub.

## Solutions

### Solution 1 : Pousser séparément (Recommandé pour l'instant)

```bash
# Pousser vers GitHub (fonctionne)
git push github main

# Pousser vers GitLab (quand la connexion fonctionne)
git push origin main
```

### Solution 2 : Utiliser SSH pour GitLab

Si HTTPS ne fonctionne pas, utilisez SSH :

```bash
# 1. Générer une clé SSH (si pas déjà fait)
ssh-keygen -t ed25519 -C "hchakra8@gmail.com"

# 2. Copier la clé publique
# Windows PowerShell:
Get-Content C:\Users\$env:USERNAME\.ssh\id_ed25519.pub

# 3. Ajouter la clé sur GitLab :
#    https://gitlab.com/-/profile/keys

# 4. Changer le remote GitLab vers SSH
git remote set-url origin git@gitlab.com:chakrahossam-group/prioritest.git

# 5. Tester
git push origin main
```

### Solution 3 : Script PowerShell pour pousser vers les deux

Créez un fichier `push-both.ps1` :

```powershell
# Pousser vers GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push github main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub push successful" -ForegroundColor Green
} else {
    Write-Host "❌ GitHub push failed" -ForegroundColor Red
}

# Pousser vers GitLab
Write-Host "Pushing to GitLab..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitLab push successful" -ForegroundColor Green
} else {
    Write-Host "⚠️ GitLab push failed (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Push completed!" -ForegroundColor Green
```

Utilisation :
```powershell
.\push-both.ps1
```

## Vérification

Pour vérifier que les deux repos sont à jour :

- **GitHub** : https://github.com/CHAKRAhossam/prioritest
- **GitLab** : https://gitlab.com/chakrahossam-group/prioritest

## Note

Une fois que GitLab fonctionne (via SSH ou après résolution du problème réseau), la commande `git push origin main` poussera automatiquement vers les deux repos grâce à la configuration des deux `pushurl`.

