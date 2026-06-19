import json
import os 
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from typing import Any
from solarmboa_graph.client import  get_session


load_dotenv() 

DISTRIBUTOR = os.getenv("DISTRIBUTOR")
GRAPH = os.getenv("GRAPH")
TECHNICIANS = os.getenv("TECHNICIANS")
INSTALLATION_JSON = os.getenv("INSTALLATION_JSON")

# def run_write(query: str, rows: list[dict]):
#     driver = get_driver()

#     with driver.session() as session:
#         session.execute_write(
#             lambda tx: tx.run(query, rows=rows).consume()
#         )

def run_query(query:str, rows: list[dict]):
    with get_session() as session:
        session.run(query, rows=rows)
        
def read_json(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
       

def import_regions():
    print("Importation des Régions...")
    
    df_distributor = pd.read_csv(DISTRIBUTOR)
    df_technicians = pd.read_csv(TECHNICIANS)
    installations = read_json(INSTALLATION_JSON)    
       
    regions = set() 
    
    regions.update(df_distributor['region'].dropna().unique())
    regions.update(df_technicians['region'].dropna().unique())   
    
    for inst in installations:
        region = inst.get("region")
        if inst.get("region"):
            regions.add(str(region).strip())
            
    rows = [{"name":region} for region in sorted(regions)if region]
    
    query = """
        UNWIND $rows AS row
        MERGE (r:Region {name: row.name})    
    """        
    
    run_query(query, rows)
    print(f"Regions importés : {len(rows)}")

def import_distributors():
    print("Importation des Distributeurs...")
    
    df = pd.read_csv(DISTRIBUTOR)

    rows = []
    for row in df.to_dict("records"):
        rows.append(
            {
                "id": str(row["id"]).strip(),
                "type": str(row.get("type", "")).strip(),
                "name": str(row.get("name", "")).strip(),
                "region": str(row.get("region", "")).strip(),
                "since": str(row.get("since", "")).strip(),
            }
        )

    query = """
    UNWIND $rows AS row
    MERGE (d:Distributor {id: row.id})
    SET d.name = row.name,
        d.type = row.type,
        d.region = row.region,
        d.since = row.since
    """

    run_query(query, rows)
    print(f"Distributeurs importés : {len(rows)}")


def import_technicians():
    print("Importation des Techniciens...")
    df = pd.read_csv(TECHNICIANS)

    rows = []
    for row in df.to_dict("records"):
        rows.append(
            {
                "id": str(row["id"]).strip(),
                "type": str(row.get("type", "")).strip(),
                "name": str(row.get("name", "")).strip(),
                "region": str(row.get("region", "")).strip(),
                "phone": str(row.get("phone", "")).strip(),
                "certified": row.get("certified"),
            }
        )

    query = """
    UNWIND $rows AS row
    MERGE (t:Technician {id: row.id})
    SET t.name = row.name,
        t.type = row.type,
        t.region = row.region,
        t.phone = row.phone,
        t.certified = row.certified
    """

    run_query(query, rows)
    print(f"Techniciens importés : {len(rows)}")


def import_installations():
    data = read_json(INSTALLATION_JSON)

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
                "gps_lat": float(item.get("gps_lat")) if item.get("gps_lat") else None,
                "gps_lon": float(item.get("gps_lon")) if item.get("gps_lon") else None,
                "install_date": item.get("install_date")
            }
        )

    query = """
    UNWIND $rows AS row
    MERGE (i:Installation {installation_id: toInteger(row.installation_id)})
    SET i.client_name = row.client_name,
        i.client_type = row.client_type,
        i.city = row.city,
        i.region = row.region,
        i.gps_lat = toFloat(row.gps_lat),
        i.gps_lon = toFloat(row.gps_lon),
        i.install_date = row.install_date,
        i.tariff_plan = row.tariff_plan,
        i.status = row.status
    """

    run_query(query, rows)
    print(f"Installations importées : {len(rows)}")



def import_region_relationships() -> None:
    print("Importation des relations régionales...")

    queries = [
        """
        MATCH (d:Distributor)
        MATCH (r:Region {name: d.region})
        MERGE (d)-[:OPERATES_IN]->(r)
        """,
        """
        MATCH (t:Technician)
        MATCH (r:Region {name: t.region})
        MERGE (t)-[:OPERATES_IN]->(r)
        """,
        """
        MATCH (i:Installation)
        MATCH (r:Region {name: i.region})
        MERGE (i)-[:LOCATED_IN]->(r)
        """,
    ]

    with get_session() as session:
        for query in queries:
            result = session.run(query)
            summary = result.consume()
            print(f"Relations créées/validées : {summary.counters.relationships_created}")


def import_relationships():
    print("Importation des Relations...")
    
    df = pd.read_csv(GRAPH)

    rows = df.fillna("").to_dict("records")

    grouped = df.groupby(['source_type', 'target_type', 'relation'])
    
    total_imported = 0
    
    for (source_type, target_type, relation), group_df in grouped:
        rows = group_df.fillna("").to_dict("records")
        
        if source_type == "distributor" and target_type == "installation" and relation == "SOLD":
            query = """
            UNWIND $rows AS r
            MATCH (d:Distributor {id: r.source_id})
            MATCH (i:Installation {installation_id: toInteger(r.target_id)})
            MERGE (d)-[rel:SOLD]->(i)
            SET rel.date = r.date, 
                rel.weight = CASE
                    WHEN r.weight = "" THEN null
                    ELSE toFloat(r.weight)
                END
            """
        elif source_type == "technician" and target_type == "installation" and relation == "MAINTAINS":
            query = """
            UNWIND $rows AS r
            MATCH (t:Technician {id: r.source_id})
            MATCH (i:Installation {installation_id: toInteger(r.target_id)})
            MERGE (t)-[rel:MAINTAINS]->(i)
            SET rel.date = r.date, 
                rel.weight = CASE
                    WHEN r.weight = "" THEN null
                    ELSE toFloat(r.weight)
                END
            """
        elif source_type == "distributor" and target_type == "technician" and relation == "EMPLOYS":
            query = """
            UNWIND $rows AS r
            MATCH (d:Distributor {id: r.source_id})
            MATCH (t:Technician {id: r.target_id})
            MERGE (d)-[rel:EMPLOYS]->(t)
            SET rel.date = r.date, 
                rel.weight = CASE
                    WHEN r.weight = "" THEN null
                    ELSE toFloat(r.weight)
                END
            """
        else:
            print(f"Relation ignorée : {source_type} -> {target_type} ({relation})")
            continue

        run_query(query, rows)
        total_imported += len(rows)
        
        print(
            f"Relations {source_type}->{target_type} "
            f"({relation}) importées : {len(rows)}"
        )
        
    print(f"Total relations importées : {total_imported}")


def import_all():
    print("DÉBUT DE L'IMPORT NEO4J\n" + "-"*40)
    import_regions() 
    import_distributors()
    import_technicians()
    import_installations()
    import_region_relationships()
    import_relationships()
    print("\n" + "="*40)
    print("Import Neo4j terminé.")


if __name__ == "__main__":
    import_all()