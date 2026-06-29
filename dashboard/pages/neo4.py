import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEO4J_SRC = PROJECT_ROOT / "Neo4JDB" / "src"
sys.path.append(str(NEO4J_SRC))

from solarmboa_graph.client import get_session


st.set_page_config(
    page_title="Neo4j - SolarMboa",
    page_icon="🕸️",
    layout="wide",
)

st.title("🕸️ Neo4j — Réseau opérationnel SolarMboa")

st.markdown(
    """
    Neo4j modélise les relations entre distributeurs, techniciens, installations et régions.
    Il sert à comprendre le réseau terrain : ventes, maintenance, couverture régionale et anomalies relationnelles.
    """
)


def run_query(query: str, params: dict | None = None) -> pd.DataFrame:
    with get_session() as session:
        result = session.run(query, params or {})
        rows = [record.data() for record in result]

    return pd.DataFrame(rows)


tab_overview, tab_distributors, tab_technicians, tab_anomalies, tab_explore = st.tabs(
    [
        "Vue d’ensemble",
        "Distributeurs",
        "Techniciens",
        "Anomalies réseau",
        "Exploration",
    ]
)


with tab_overview:
    st.header("Vue d’ensemble du graphe")

    df_nodes = run_query(
        """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS total
        ORDER BY total DESC
        """
    )

    df_rels = run_query(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS relation, count(r) AS total
        ORDER BY total DESC
        """
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Types de nœuds", len(df_nodes))
    c2.metric("Nombre de relations", int(df_rels["total"].sum()) if not df_rels.empty else 0)
    c3.metric("Types de relations", len(df_rels))

    st.subheader("Nœuds par type")
    st.dataframe(df_nodes, use_container_width=True)

    if not df_nodes.empty:
        st.bar_chart(df_nodes.set_index("label")["total"])

    st.subheader("Relations par type")
    st.dataframe(df_rels, use_container_width=True)

    if not df_rels.empty:
        st.bar_chart(df_rels.set_index("relation")["total"])


with tab_distributors:
    st.header("Top distributeurs")

    df_top_dist = run_query(
        """
        MATCH (d:Distributor)-[:SOLD]->(i:Installation)
        RETURN d.id AS distributor_id,
               d.name AS distributor_name,
               d.region AS region,
               count(i) AS installations_sold
        ORDER BY installations_sold DESC
        LIMIT 20
        """
    )

    if df_top_dist.empty:
        st.warning("Aucune relation SOLD trouvée.")
    else:
        st.dataframe(df_top_dist, use_container_width=True)
        st.bar_chart(df_top_dist.set_index("distributor_name")["installations_sold"])

    st.subheader("Détail d’un distributeur")

    distributor_id = st.text_input("Distributor ID", value="DIST-001")

    if st.button("Afficher les installations vendues"):
        df_detail = run_query(
            """
            MATCH (d:Distributor {id: $distributor_id})-[:SOLD]->(i:Installation)
            RETURN i.installation_id AS installation_id,
                   i.client_name AS client_name,
                   i.region AS region,
                   i.status AS status,
                   i.tariff_plan AS tariff_plan
            ORDER BY i.installation_id
            """,
            {"distributor_id": distributor_id},
        )

        st.write(f"{len(df_detail)} installation(s) trouvée(s)")
        st.dataframe(df_detail, use_container_width=True)


with tab_technicians:
    st.header("Top techniciens")

    df_top_tech = run_query(
        """
        MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
        RETURN t.id AS technician_id,
               t.name AS technician_name,
               t.region AS region,
               t.certified AS certified,
               count(i) AS installations_maintained
        ORDER BY installations_maintained DESC
        LIMIT 20
        """
    )

    if df_top_tech.empty:
        st.warning("Aucune relation MAINTAINS trouvée.")
    else:
        st.dataframe(df_top_tech, use_container_width=True)
        st.bar_chart(df_top_tech.set_index("technician_name")["installations_maintained"])

    st.subheader("Détail d’un technicien")

    technician_id = st.text_input("Technician ID", value="TECH-0001")


    if st.button("Afficher les installations maintenues"):
        df_detail = run_query(
            """
            MATCH (t:Technician {id: $technician_id})-[:MAINTAINS]->(i:Installation)
            RETURN i.installation_id AS installation_id,
                   i.client_name AS client_name,
                   i.region AS region,
                   i.status AS status,
                   i.tariff_plan AS tariff_plan
            ORDER BY i.installation_id
            """,
            {"technician_id": technician_id},
        )

        st.write(f"{len(df_detail)} installation(s) trouvée(s)")
        st.dataframe(df_detail, use_container_width=True)


with tab_anomalies:
    st.header("Anomalies réseau")

    st.subheader("Installations sans technicien")

    df_without_tech = run_query(
        """
        MATCH (i:Installation)
        WHERE NOT EXISTS {
          MATCH (:Technician)-[:MAINTAINS]->(i)
        }
        RETURN i.installation_id AS installation_id,
               i.region AS region,
               i.status AS status
        """
    )

    st.metric("Installations sans technicien", len(df_without_tech))
    st.dataframe(df_without_tech, use_container_width=True)

    st.subheader("Ventes hors région")

    df_cross_region = run_query(
        """
        MATCH (d:Distributor)-[:SOLD]->(i:Installation)
        WHERE d.region <> i.region
        RETURN d.id AS distributor_id,
               d.name AS distributor_name,
               d.region AS distributor_region,
               i.installation_id AS installation_id,
               i.region AS installation_region
        """
    )

    st.metric("Ventes hors région", len(df_cross_region))
    st.dataframe(df_cross_region, use_container_width=True)


with tab_explore:
    st.header("Exploration du graphe")

    st.markdown(
        """
        Cette section affiche des chemins simples entre distributeurs, techniciens et installations.
        Pour une visualisation graphe avancée, utilise aussi Neo4j Browser.
        """
    )

    df_paths = run_query(
        """
        MATCH path = (d:Distributor)-[:EMPLOYS]->(t:Technician)-[:MAINTAINS]->(i:Installation)
        RETURN d.id AS distributor_id,
               d.name AS distributor,
               t.id AS technician_id,
               t.name AS technician,
               i.installation_id AS installation_id,
               i.region AS installation_region
        LIMIT 100
        """
    )
    
    df_region = run_query(
        """
        MATCH (i:Installation)-[:LOCATED_IN]->(r:Region) 
        RETURN r.name As region,count(i) As total ;
        """
    )
    
    
    if not df_region.empty:
        df_region = df_region.rename(columns={"_id":"installation"})
        st.dataframe(df_region, use_container_width=True)
        st.bar_chart(df_region.set_index('region')['total'])
    
    # if df_region.empty:
    #     st.warning("Aucune relation MAINTAINS trouvée.")
    # else:
    #     st.dataframe(df_region, use_container_width=True)
    #     st.bar_chart(df_region.set_index("technician_name")["installations_maintained"])
        
    if df_paths.empty:
        st.info("Aucun chemin Distributor → Technician → Installation trouvé.")
    else:
        st.dataframe(df_paths, use_container_width=True)