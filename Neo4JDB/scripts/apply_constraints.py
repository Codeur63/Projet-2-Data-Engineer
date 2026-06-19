from pathlib import Path
from neo4j.exceptions import ClientError
from solarmboa_graph.client import get_driver,get_session


CYPHER_PATH = Path("Neo4JDB/cypher/constraints.cypher")


def main():
    if not CYPHER_PATH.exists():
        print(f"Erreur : Fichier introuvable à {CYPHER_PATH}")
        return

    driver = get_driver()
    cypher_text = CYPHER_PATH.read_text(encoding="utf-8")

    statements = [
        stmt.strip()
        for stmt in cypher_text.split(";")
        if stmt.strip()
    ]

    print(f"Exécution de {len(statements)} requête(s)...\n")

    with get_session() as session:
        for stmt in statements:
            try:
                session.run(stmt)
                print(f"OK : {stmt.split(chr(10))[0].strip()}")
                
            except ClientError as e:
                if "EquivalentSchemaRuleAlreadyExists" in str(e):
                    print(f" Déjà existant : {stmt.split(chr(10))[0].strip()}")
                else:
                    print(f"Erreur sur : {e.message}")

    print("\nContraintes et index Neo4j appliqués.")
    driver.close()


if __name__ == "__main__":
    main()