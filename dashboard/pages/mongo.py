import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONGODB_SRC = PROJECT_ROOT / "MongoDB" / "src"
sys.path.append(str(MONGODB_SRC))

from solarmboa.database import get_db


st.set_page_config(
    page_title="MongoDB - SolarMboa",
    page_icon="🍃",
    layout="wide",
)

st.title("🍃 MongoDB — Profils d’installations SolarMboa")

st.markdown(
    """
    MongoDB stocke les profils enrichis des installations :
    clients, contrats, localisation, équipements, maintenance et indicateurs business.
    """
)

db = get_db()
col = db["installations"]

tab_overview, tab_business, tab_anomalies, tab_search = st.tabs(
    ["Vue d’ensemble", "Business", "Anomalies", "Recherche"]
)


# ======================================================
# 1. OVERVIEW
# ======================================================

with tab_overview:
    st.header("État global MongoDB")

    total = col.count_documents({})
    active = col.count_documents({"status": "active"})
    maintenance = col.count_documents({"status": "maintenance"})
    suspended = col.count_documents({"status": "suspended"})

    revenue_pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "ca": {"$sum": "$contract.monthly_xaf"}}},
    ]
    revenue_result = list(col.aggregate(revenue_pipeline))
    ca_total = revenue_result[0]["ca"] if revenue_result else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Installations", f"{total:,}")
    c2.metric("Actives", f"{active:,}")
    c3.metric("Maintenance", f"{maintenance:,}")
    c4.metric("CA mensuel actif", f"{ca_total:,.0f} XAF")

    st.subheader("Répartition par statut")

    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    df_status = pd.DataFrame(list(col.aggregate(status_pipeline)))

    if not df_status.empty:
        df_status = df_status.rename(columns={"_id": "status"})
        st.dataframe(df_status, use_container_width=True)
        st.bar_chart(df_status.set_index("status")["count"])


# ======================================================
# 2. BUSINESS
# ======================================================

with tab_business:
    st.header("Indicateurs business")

    st.subheader("CA mensuel par région")

    region_pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$location.region",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
    ]

    df_region = pd.DataFrame(list(col.aggregate(region_pipeline)))

    if not df_region.empty:
        df_region = df_region.rename(columns={"_id": "region"})
        st.dataframe(df_region, use_container_width=True)
        st.bar_chart(df_region.set_index("region")["ca_total"])

    st.subheader("CA mensuel par plan tarifaire")

    plan_pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$contract.plan",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
    ]

    df_plan = pd.DataFrame(list(col.aggregate(plan_pipeline)))

    if not df_plan.empty:
        df_plan = df_plan.rename(columns={"_id": "plan"})
        st.dataframe(df_plan, use_container_width=True)
        st.bar_chart(df_plan.set_index("plan")["ca_total"])

    st.subheader("Top 10 distributeurs par CA")

    distributor_pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$distributor_id",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
        {"$limit": 10},
    ]

    df_distributor = pd.DataFrame(list(col.aggregate(distributor_pipeline)))

    if not df_distributor.empty:
        df_distributor = df_distributor.rename(columns={"_id": "distributor_id"})
        st.dataframe(df_distributor, use_container_width=True)
        st.bar_chart(df_distributor.set_index("distributor_id")["ca_total"])


# ======================================================
# 3. ANOMALIES
# ======================================================

with tab_anomalies:
    st.header("Anomalies opérationnelles")

    st.subheader("Installations sans GPS")

    no_gps_pipeline = [
        {
            "$match": {
                "$or": [
                    {"location.gps": {"$exists": False}},
                    {"location.gps.coordinates.0": None},
                    {"location.gps.coordinates.1": None},
                    {"location.gps_available": False},
                ]
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "client_type": 1,
                "location.city": 1,
                "location.region": 1,
            }
        },
    ]

    df_no_gps = pd.DataFrame(list(col.aggregate(no_gps_pipeline)))
    st.metric("Sans GPS", len(df_no_gps))
    st.dataframe(df_no_gps, use_container_width=True)

    st.subheader("Installations avec plus de 3 maintenances correctives")

    corrective_pipeline = [
        {
            "$addFields": {
                "corrective_count": {
                    "$size": {
                        "$filter": {
                            "input": "$maintenance_history",
                            "as": "m",
                            "cond": {"$eq": ["$$m.type", "corrective"]},
                        }
                    }
                }
            }
        },
        {"$match": {"corrective_count": {"$gt": 3}}},
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "status": 1,
                "corrective_count": 1,
                "location.region": 1,
            }
        },
        {"$sort": {"corrective_count": -1}},
    ]

    df_corrective = pd.DataFrame(list(col.aggregate(corrective_pipeline)))
    st.metric("Maintenances excessives", len(df_corrective))
    st.dataframe(df_corrective, use_container_width=True)

    st.subheader("Passages Standard → Premium")

    upgrade_pipeline = [
        {
            "$match": {
                "contract.history": {
                    "$elemMatch": {
                        "from_plan": "Standard",
                        "to_plan": "Premium",
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "contract.plan": 1,
                "contract.history": 1,
                "contract.monthly_xaf": 1,
            }
        },
    ]

    df_upgrade = pd.DataFrame(list(col.aggregate(upgrade_pipeline)))
    st.metric("Upgrades détectés", len(df_upgrade))
    st.dataframe(df_upgrade, use_container_width=True)


# ======================================================
# 4. SEARCH
# ======================================================

with tab_search:
    st.header("Recherche d’installations")

    col1, col2, col3 = st.columns(3)

    region = col1.text_input("Région", "")
    status = col2.selectbox(
        "Statut",
        ["", "active", "maintenance", "suspended", "churned", "pending"],
    )
    plan = col3.selectbox(
        "Plan",
        ["", "Basic", "Standard", "Premium", "Custom"],
    )

    query = {}

    if region:
        query["location.region"] = region
    if status:
        query["status"] = status
    if plan:
        query["contract.plan"] = plan

    limit = st.slider("Nombre de résultats", 10, 100, 30)

    docs = list(
        col.find(
            query,
            {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "client_type": 1,
                "status": 1,
                "location.region": 1,
                "location.city": 1,
                "contract.plan": 1,
                "contract.monthly_xaf": 1,
            },
        )
        .sort("installation_id", 1)
        .limit(limit)
    )

    st.write(f"{len(docs)} résultat(s)")
    st.dataframe(pd.DataFrame(docs), use_container_width=True)