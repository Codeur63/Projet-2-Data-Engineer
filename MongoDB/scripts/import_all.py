"""
Lance l'import complet : installations.json -> MongoDB local.
A executer une seule fois (ou apres drop de la collection).
"""

import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from solarmboa.database import get_db, verifier_connexion
from solarmboa.services.importer import ImportPipeline

load_dotenv()

def main():
    # 1. Verifier que MongoDB tourne
    etat = verifier_connexion()

    print(f"MongoDB : {etat}")
    if etat["statut"] != "connecting ... OK":
        print("ERREUR : Connexion pas etablie avec MongoDB")
        print("Demarrer MongoDB :")
        print(" Windows : Start-Service MongoDB (PowerShell admin)")
        print(" macOS : brew services start mongodb-community@7.0")
        print(" Linux : sudo systemctl start mongod")
        sys.exit(1)

    # 2. Preparer la collection
    db = get_db()
    json_path = Path(os.getenv("INSTALLATION_JSON"))
    if not json_path.exists():
        print(f"ERREUR : {json_path} introuvable.")
        print("Copier le fichier installations.json dans data/raw/")
        sys.exit(1)

    # 3. Option : vider la collection avant reimport
    nb_existants = db["installations"].count_documents({})
    if nb_existants > 0:
        rep = input(f"{nb_existants:,} documents deja presents. Reimporter ? (o/n) : ")
        if rep.lower() == "o":
            db["installations"].drop()
            print("Collection supprimee.")
        else:
            print("Import annule.")
            return

    # 4. Lancer l'import
    print(f"Import dscepuis : {json_path}")
    pipeline = ImportPipeline(db["installations"])
    rapport = pipeline.run(str(json_path))

    # 5. Afficher le rapport
    print()
    print("=" * 50)
    print(" RAPPORT D'IMPORT SOLARMBOA")
    print("=" * 50)
    print(f'Total brut : {rapport["total_brut"]:,}')
    print(f'Doublons trouves: {rapport["doublons"]:,}')
    print(f'Inseres : {rapport["inseres"]:,}')
    print(f'Ignores  : {rapport["ignores"]:,}')
    print(f'Avertissements : {rapport["avertissements"]:,}')
    print()
    print("Distribution par type :", rapport["distribution_type"])
    print("Distribution par statut:", rapport["distribution_statut"])

    if rapport["top_warns"]:
        print()
        print("Top 10 avertissements :")
        for w in rapport["top_warns"]:
            print(f"- {w}")


if __name__ == "__main__":
    main()
