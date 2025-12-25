# Génération des Diagrammes Simplifiés S6 et S7

## Fichiers créés

- `use_case_s6_simple.puml` - Diagramme de cas d'utilisation simplifié pour S6
- `use_case_s7_simple.puml` - Diagramme de cas d'utilisation simplifié pour S7
- `class_s6_simple.puml` - Diagramme de classes simplifié pour S6
- `class_s7_simple.puml` - Diagramme de classes simplifié pour S7

## Génération des images PNG

### Méthode 1 : PlantUML en ligne de commande

#### Windows (PowerShell)
```powershell
cd docs/diagrams
.\generate_diagrams.ps1
```

#### Linux/Mac
```bash
cd docs/diagrams
chmod +x generate_diagrams.sh
./generate_diagrams.sh
```

### Méthode 2 : PlantUML en ligne

1. Ouvrir https://www.plantuml.com/plantuml/uml/
2. Copier le contenu d'un fichier `.puml`
3. Coller dans l'éditeur
4. Cliquer sur "Submit" pour générer
5. Télécharger l'image PNG

### Méthode 3 : Avec Java et plantuml.jar

```bash
# Télécharger plantuml.jar depuis https://plantuml.com/download
java -jar plantuml.jar -tpng use_case_s6_simple.puml
java -jar plantuml.jar -tpng use_case_s7_simple.puml
java -jar plantuml.jar -tpng class_s6_simple.puml
java -jar plantuml.jar -tpng class_s7_simple.puml
```

### Méthode 4 : VS Code Extension

1. Installer l'extension "PlantUML" dans VS Code
2. Ouvrir un fichier `.puml`
3. Appuyer sur `Alt+D` pour prévisualiser
4. Exporter en PNG via le menu contextuel

## Fichiers de sortie attendus

Après génération, vous devriez avoir :
- `use_case_s6_simple.png`
- `use_case_s7_simple.png`
- `class_s6_simple.png`
- `class_s7_simple.png`

Ces fichiers peuvent ensuite être utilisés dans le rapport LaTeX.















