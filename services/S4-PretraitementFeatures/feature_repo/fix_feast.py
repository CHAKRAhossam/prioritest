import sys
from feast.cli import cli

print("Tentative d'exécution de 'feast apply' via Python...")

# On simule la commande "feast apply" que tu aurais tapée dans le terminal
sys.argv = ["feast", "apply"]

try:
    # On lance l'outil interne de Feast
    cli()
    print("\n✅ SUCCÈS : La configuration Feast a été appliquée !")
except SystemExit as e:
    if e.code == 0:
        print("\n✅ SUCCÈS : La configuration Feast a été appliquée !")
    else:
        print(f"\n❌ ÉCHEC : Feast a quitté avec le code {e.code}")
except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE : {e}")