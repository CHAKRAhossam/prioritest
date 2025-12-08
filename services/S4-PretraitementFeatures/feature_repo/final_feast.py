import sys
import os

# On simule les arguments de la ligne de commande
sys.argv = ["feast", "apply"]

# Changer le dossier de travail vers le dossier du script (feature_repo)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"Working dir: {os.getcwd()}")
print("🛠️  Tentative de réparation et lancement de Feast...")

try:
    print("👉 Importation de feast.cli.cli...")
    from feast.cli import cli as cli_module
    
    if hasattr(cli_module, "cli") and callable(cli_module.cli):
        print("✅ Fonction 'cli' trouvée dans le module. Lancement...")
        cli_module.cli()
    else:
        print("⚠️ Fonction 'cli' non trouvée. Inspection du module...")
        print(dir(cli_module))
        raise Exception("Impossible de trouver le point d'entrée CLI.")

    print("\n✅ SUCCÈS : Configuration Feast appliquée avec succès !")

except SystemExit as e:
    if e.code == 0:
        print("\n✅ SUCCÈS : Opération terminée sans erreur !")
    else:
        print(f"\n❌ ÉCHEC : Feast a quitté avec le code {e.code}")
except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE : {e}")
