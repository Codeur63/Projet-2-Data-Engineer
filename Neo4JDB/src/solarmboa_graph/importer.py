import json
import os 
from dotenv import load_dotenv
import pandas as pd
from .client import get_driver, get_session


load_dotenv() 




def run_write(query: str, rows: list[dict]):
    driver = get_driver()

    with get.session() as session:
        session.execute_write(
            lambda tx: tx.run(query, rows=rows).consume()
        )


def import_distributors():
    path = DATA_RAW / "network_nodes_distributors.csv"
    df = pd.read_csv(path)

    rows = df.fillna("").to_dict("records")

    query = """
    UNWIND $rows AS row
    MERGE (d:Distributor {id: row.id})
    SET d.name = row.name,
        d.region = row.region,
        d.since = row.since
    """

    run_write(query, rows)
    print(f"Distributeurs importés : {len(rows)}")


def import_technicians():
    path = DATA_RAW / "network_nodes_technicians.csv"
    df = pd.read_csv(path)

    rows = df.fillna("").to_dict("records")

    query = """
    UNWIND $rows AS row
    MERGE (t:Technician {id: row.id})
    SET t.name = row.name,
        t.region = row.region,
        t.phone = row.phone,
        t.certified = row.certified
    """

    run_write(query, rows)
    print(f"Techniciens importés : {len(rows)}")


def import_installations():
    path = DATA_RAW / "installations.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for item in data:
        rows.append(
            {
                "installation_id": int(item.get("installation_id")),
                "client_name": item.get("client_name"),
                "client_type": item.get("client_type"),
                "status": item.get("status"),
                "region": item.get("region"),
                "city": item.get("city"),
                "tariff_plan": item.get("tariff_plan"),
            }
        )

    query = """
    UNWIND $rows AS row
    MERGE (i:Installation {installation_id: row.installation_id})
    SET i.client_name = row.client_name,
        i.client_type = row.client_type,
        i.status = row.status,
        i.region = row.region,
        i.city = row.city,
        i.tariff_plan = row.tariff_plan
    """

    run_write(query, rows)
    print(f"Installations importées : {len(rows)}")


def import_relationships():
    path = DATA_RAW / "network_graph.csv"
    df = pd.read_csv(path)

    rows = df.fillna("").to_dict("records")

    driver = get_driver()

    with driver.session() as session:
        for row in rows:
            source_type = row["source_type"]
            target_type = row["target_type"]
            relation = row["relation"]

            if source_type == "distributor" and target_type == "installation":
                session.execute_write(
                    lambda tx, r: tx.run(
                        """
                        MATCH (d:Distributor {id: r.source_id})
                        MATCH (i:Installation {installation_id: toInteger(r.target_id)})
                        MERGE (d)-[rel:SOLD]->(i)
                        SET rel.date = r.date,
                            rel.weight = r.weight
                        """,
                        r=row,
                    ).consume()
                )

            elif source_type == "technician" and target_type == "installation":
                session.execute_write(
                    lambda tx, r: tx.run(
                        """
                        MATCH (t:Technician {id: r.source_id})
                        MATCH (i:Installation {installation_id: toInteger(r.target_id)})
                        MERGE (t)-[rel:MAINTAINS]->(i)
                        SET rel.date = r.date,
                            rel.weight = r.weight
                        """,
                        r=row,
                    ).consume()
                )

            elif source_type == "distributor" and target_type == "technician":
                session.execute_write(
                    lambda tx, r: tx.run(
                        """
                        MATCH (d:Distributor {id: r.source_id})
                        MATCH (t:Technician {id: r.target_id})
                        MERGE (d)-[rel:WORKS_WITH]->(t)
                        SET rel.date = r.date,
                            rel.weight = r.weight
                        """,
                        r=row,
                    ).consume()
                )

    print(f"Relations importées : {len(rows)}")


def import_all():
    import_distributors()
    import_technicians()
    import_installations()
    import_relationships()
    print("Import Neo4j terminé.")


if __name__ == "__main__":
    import_all()