# Compilation du Rapport LaTeX PRIORITEST

## Prérequis

- Distribution LaTeX installée (TeX Live, MiKTeX, ou MacTeX)
- Packages LaTeX requis :
  - babel (french)
  - inputenc, fontenc
  - graphicx, float, caption
  - fancyhdr, hyperref
  - geometry, placeins
  - etoolbox

## Structure des fichiers

```
docs/
├── RAPPORT_PRIORITEST.tex    # Fichier principal
├── rapport.cls                # Classe LaTeX personnalisée
└── logos/
    └── EMSI.png              # Logo (à ajouter)
```

## Compilation

### Méthode 1 : Compilation directe

```bash
cd docs
pdflatex RAPPORT_PRIORITEST.tex
pdflatex RAPPORT_PRIORITEST.tex  # Deuxième passe pour les références
```

### Méthode 2 : Avec Makefile

```bash
cd docs
make rapport
```

### Méthode 3 : Avec un éditeur LaTeX

- Ouvrir `RAPPORT_PRIORITEST.tex` dans votre éditeur LaTeX préféré (TeXstudio, Overleaf, etc.)
- Compiler avec le bouton de compilation

## Notes importantes

1. **Logo** : Assurez-vous que le fichier `logos/EMSI.png` existe. Si le logo est dans un autre emplacement, modifiez la ligne `\logo{logos/EMSI.png}` dans le fichier `.tex`.

2. **Images** : Si vous souhaitez ajouter des diagrammes ou captures d'écran, placez-les dans un dossier `screens/` et utilisez la commande :
   ```latex
   \insererfigure{screens/mon-image.png}{8cm}{Ma légende}{mon-label}
   ```

3. **Références croisées** : La compilation nécessite deux passes pour résoudre toutes les références (sections, figures, etc.).

## Résolution des problèmes

### Erreur "File 'rapport.cls' not found"
- Assurez-vous que `rapport.cls` est dans le même répertoire que `RAPPORT_PRIORITEST.tex`
- Ou utilisez `TEXINPUTS` pour spécifier le chemin :
  ```bash
  export TEXINPUTS=./docs:
  ```

### Erreur "File 'logos/EMSI.png' not found"
- Créez le dossier `logos/` dans `docs/`
- Ajoutez le logo `EMSI.png` dans ce dossier
- Ou modifiez le chemin dans le fichier `.tex`

### Erreur de package manquant
- Installez les packages manquants via votre gestionnaire de packages LaTeX
- Pour TeX Live : `tlmgr install <package>`
- Pour MiKTeX : Utilisez l'interface graphique MiKTeX Package Manager

## Personnalisation

Pour modifier les informations du rapport, éditez les lignes suivantes dans `RAPPORT_PRIORITEST.tex` :

```latex
\logo{logos/EMSI.png}
\unif{EMSI Marrakech}
\titre{PRIORITEST — ...}
\cours{Développement multiplateforme}
\enseignant{Hanae \textsc{Sbai}}
\eleves{Hicham \textsc{Kaou} \\ ...}
```















