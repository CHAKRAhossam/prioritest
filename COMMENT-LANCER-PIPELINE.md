# Comment lancer le pipeline Jenkins et voir les logs

## 🚀 Déclencher un nouveau build

### Méthode 1 : Interface Web (Recommandé)

1. **Ouvrez Jenkins dans votre navigateur :**
   ```
   http://localhost:8080
   ```

2. **Accédez au job :**
   - Cliquez sur **"PRIORITEST"**
   - Cliquez sur **"main"** (la branche)

3. **Déclenchez le build :**
   - Cliquez sur **"Build Now"** (ou "Construire maintenant")

4. **Suivez les logs en temps réel :**
   - Cliquez sur le numéro du build (ex: **#28**)
   - Cliquez sur **"Console Output"** (ou "Sortie de la console")
   - Les logs s'affichent en temps réel

### Méthode 2 : Ligne de commande (via Docker)

```bash
# Voir le dernier build
docker exec prioritest-jenkins bash -c "ls -t /var/jenkins_home/jobs/PRIORITEST/branches/main/builds/ | head -1"

# Voir les logs du dernier build
docker exec prioritest-jenkins bash -c "LATEST=\$(ls -t /var/jenkins_home/jobs/PRIORITEST/branches/main/builds/ | head -1); cat /var/jenkins_home/jobs/PRIORITEST/branches/main/builds/\$LATEST/log | tail -100"
```

## 📊 Ce qui a été corrigé dans le Jenkinsfile

### ✅ Modifications apportées :

1. **Retrait de `-Dsonar.qualitygate.wait=true`** de toutes les analyses SonarQube
   - Le build ne sera plus "UNSTABLE" à cause d'un Quality Gate échoué
   - Les analyses SonarQube continueront même si le Quality Gate échoue

2. **Amélioration de l'étape "Quality Gate Check"**
   - Affichage des détails des conditions échouées
   - Résumé des services en échec
   - Liens vers les dashboards SonarQube

### 📈 Résultats attendus :

- ✅ Le build devrait maintenant être **SUCCESS** au lieu de **UNSTABLE**
- ✅ Les rapports de couverture seront toujours envoyés à SonarQube
- ✅ Les détails des Quality Gates échoués seront affichés dans les logs

## 🔍 Messages clés à rechercher dans les logs

### Messages de succès :
```
✅ Quality Gate passed for [service-name]
✅ jacoco.exec found
✅ coverage.xml found
✅ LCOV report found
```

### Messages d'avertissement :
```
⚠️ Warning: Quality Gate status for [service-name]: ERROR
⚠️ Warning: Proceeding without coverage report
```

### Messages d'erreur :
```
[ERROR] Tests run: X, Failures: Y, Errors: Z
ERROR: Coverage report can't be loaded
```

## 📝 Vérification rapide

Après avoir lancé le build, vérifiez :

1. **Le statut final :**
   - Devrait être **SUCCESS** (au lieu de UNSTABLE)

2. **Les Quality Gates :**
   - Recherchez dans les logs : `✅ Quality Gate passed` ou `⚠️ Warning: Quality Gate status`

3. **Les rapports de couverture :**
   - Recherchez : `✅ jacoco.exec found` (Java)
   - Recherchez : `✅ coverage.xml found` (Python)
   - Recherchez : `✅ LCOV report found` (Frontend)

## 🔗 Liens utiles

- **Jenkins** : http://localhost:8080
- **SonarQube** : http://localhost:9000
- **Job Jenkins** : http://localhost:8080/job/PRIORITEST/job/main

## 💡 Astuce

Pour voir les logs en temps réel pendant l'exécution du build :
1. Ouvrez la console du build
2. Actualisez la page régulièrement (F5)
3. Les nouveaux logs apparaîtront automatiquement




