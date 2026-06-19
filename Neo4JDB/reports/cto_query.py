"""
Rapport CTO Neo4j — graphe SolarMboa.
"""

from pprint import pprint
from datetime import datetime

from solarmboa_graph.client import get_session


def run_query(query: str, params: dict | None = None) -> list[dict]:
    with get_session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_rows(rows: list[dict], limit: int = 10):
    if not rows:
        print("Aucun résultat.")
        return

    for row in rows[:limit]:
        pprint(row, sort_dicts=False)


def node_counts():
    return run_query("""
    MATCH (n)
    RETURN labels(n) AS labels, count(n) AS total
    ORDER BY total DESC
    """)


def relationship_counts():
    return run_query("""
    MATCH ()-[r]->()
    RETURN type(r) AS relation, count(r) AS total
    ORDER BY total DESC
    """)


def top_distributors():
    return run_query("""
    MATCH (d:Distributor)-[:SOLD]->(i:Installation)
    RETURN d.id AS distributor_id,
           d.name AS distributor_name,
           count(i) AS installations_sold
    ORDER BY installations_sold DESC
    LIMIT 10
    """)


def top_technicians():
    return run_query("""
    MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
    RETURN t.id AS technician_id,
           t.name AS technician_name,
           count(i) AS installations_maintained
    ORDER BY installations_maintained DESC
    LIMIT 10
    """)


def installations_without_technician():
    return run_query("""
    MATCH (i:Installation)
    WHERE NOT EXISTS {
      MATCH (:Technician)-[:MAINTAINS]->(i)
    }
    RETURN i.installation_id AS installation_id,
           i.region AS region,
           i.status AS status
    LIMIT 20
    """)


def cross_region_sales():
    return run_query("""
    MATCH (d:Distributor)-[:SOLD]->(i:Installation)
    WHERE d.region <> i.region
    RETURN d.name AS distributor,
           d.region AS distributor_region,
           i.installation_id AS installation_id,
           i.region AS installation_region
    LIMIT 20
    """)


def main():
    print_section("SOLARMBOA — RAPPORT CTO NEO4J")
    print(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_section("1. NŒUDS PAR TYPE")
    print_rows(node_counts())

    print_section("2. RELATIONS PAR TYPE")
    print_rows(relationship_counts())

    print_section("3. TOP DISTRIBUTEURS PAR INSTALLATIONS VENDUES")
    print_rows(top_distributors())

    print_section("4. TOP TECHNICIENS PAR INSTALLATIONS MAINTENUES")
    print_rows(top_technicians())

    print_section("5. INSTALLATIONS SANS TECHNICIEN")
    print_rows(installations_without_technician())

    print_section("6. VENTES HORS RÉGION")
    print_rows(cross_region_sales())

    print_section("CONCLUSION CTO")
    print(
        "Neo4j permet de visualiser et d'analyser le réseau opérationnel SolarMboa : "
        "distributeurs, techniciens, installations et relations terrain. "
        "Il complète MongoDB en apportant une lecture relationnelle du système."
    )


if __name__ == "__main__":
    main()