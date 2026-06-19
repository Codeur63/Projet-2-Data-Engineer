from solarmboa.database import verifier_connexion, get_db

if __name__ == "__main__":
    print("Test de connexion a MongoDB local ...\n")
    print(verifier_connexion())
    print("\nTest de connexion termine.")
    print("Acces a la base de donnees :", get_db())
