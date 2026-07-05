# import streamlit as st

# st.set_page_config(
#     page_title="SolarMboa Data Platform",
#     page_icon="☀️",
#     layout="wide",
# )



# st.markdown(
#     """
#     <div class="hero">
#         <h1 class="title">☀️ SolarMboa Data Platform</h1>
#         <p class="subtitle">
#             Construction d'une infrastructure de données d'une stratup solaire camerounaise en plein evolution 
#         </p>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown(
#     """
#     <div> 
#         <h2> Implémentation de 5 bases de données NoSQL pour l'architecture Data de la Platform </h2>
#     </div> 
#     """,
#     unsafe_allow_html=True,
# )

# col1, col2, col3 = st.columns(3)

# col4, col5 = st.columns(2) 

# with col1:
#     st.markdown(
#         """
#         <div class="card">
#             <span class="badge">Redis terminé</span>
#             <h3>⚡ Cache temps réel</h3>
#             <p>
#                 Redis accélère l'accès aux sessions capteurs, gère les TTL,
#                 la stratégie LRU, les compteurs actifs et les leaderboards.
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

# with col2:
#     st.markdown(
#         """
#         <div class="card">
#             <span class="badge">Termine</span>
#             <h3>🍃 MongoDB</h3>
#             <p>
#                 MongoDB stockera les profils enrichis des installations :
#                 équipements, contrat, client, localisation et historique qui peuvent etre différent entre capteurs
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

# with col3:
#     st.markdown(
#         """
#         <div class="card">
#             <span class="badge">Terminer </span>
#             <h3>📈 Cassandra</h3>
#             <p>
#                 Cassandra seras dedié à stocker des données :
#                 ingestion massive, métriques solaires, regions et capteurs quasi temps réel.
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
    
# with col4:
#     st.markdown(
#         """
#         <div class="card">
#             <span class="badge">Terminer </span>
#             <h3>📈 InfluxDB</h3>
#             <p>
#                 InfluxDB seront dédiées aux séries temporelles :
#                 ingestion massive,métriques solaires, et alert code temps réel.
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
    
    
# with col5:
#     st.markdown(
#         """
#         <div class="card">
#             <span class="badge">Terminer </span>
#             <h3>📈  Neo4J </h3>
#             <p>
#                 Neo4j seras dédiées aux relation entre les tables :
#                 Récupération rapide des liens entre les tables sous forme de graph ou de table.
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )    
        

# st.markdown("## Architecture cible pour solarmboa")

# st.markdown(
#     """
# ```text
# Capteurs IoT
#    ↓
# API d'ingestion
#    ↓
# Redis ───────────────► Cache sessions / compteurs actifs / leaderboard
#    ↓
# MongoDB ─────────────► Profils installations
#    ↓
# Cassandra ─────────────► Ingestion Massive des données dans un cluster
#    ↓
# InfluxDB ─────────────► Séries temporelles et métriques temps réel    
#    ↓
# Neo4j ─────────────► Relation entre les tables, Graph
#   ↓
# AWS Finops
#    ↓
# Data Lake AWS S3
#    ↓
# Data Warehouse
#    ↓
# BI / Dashboard Streamlit

# """)

# st.info("Developper le menu latéral pour ouvrir les pages de simulations des BD NoSQL.")

# st.markdown(
#     '''
#     # SolarMboa — Architecture réseau GCP

# ## Objectif

# Concevoir une infrastructure réseau sécurisée avec deux environnements séparés :

# - `solarmboa-prod-vpc`
# - `solarmboa-staging-vpc`

# Chaque environnement possède ses propres subnets, règles firewall minimales et accès contrôlés.

# ## Diagramme réseau

# ```mermaid
# flowchart TD

#     USERS[Utilisateurs / Dashboard]
#     IOT[Capteurs IoT]
    
#     USERS --> LB[HTTPS Load Balancer]
#     IOT --> LB

#     LB --> CR[Cloud Run API Ingestion]

#     subgraph PROD[solarmboa-prod-vpc]
#         CR --> PUBSUB[Pub/Sub]
#         PUBSUB --> DATAFLOW[Dataflow / Cloud Run Jobs]
#         DATAFLOW --> GCS[GCS Bronze / Silver / Gold]
#         GCS --> BQ[BigQuery]
        
#         CR --> REDIS[Memorystore Redis]
#         CR --> MONGO[MongoDB Atlas / VM privée]
#         CR --> INFLUX[InfluxDB privé]
#         CR --> NEO4J[Neo4j privé]
#         CR --> CASS[Cassandra / Bigtable alternative]
#     end

#     subgraph STAGING[solarmboa-staging-vpc]
#         CR_STG[Cloud Run Staging]
#         GCS_STG[GCS staging]
#         BQ_STG[BigQuery staging]
#     end

#     ADMIN[Admin / DevOps] --> IAP[IAP / Bastion sécurisé]
#     IAP --> PROD
#     IAP --> STAGING
# ```

# # SolarMboa — Architecture réseau AWS

# ## Objectif

# Déployer SolarMboa sur AWS avec deux environnements isolés :

# - `solarmboa-prod-vpc`
# - `solarmboa-staging-vpc`

# Chaque environnement contient des subnets publics uniquement pour l’entrée contrôlée, et des subnets privés pour les services applicatifs et data.

# ## Diagramme

# ```mermaid
# flowchart TD

#     USERS[Utilisateurs / Dashboard]
#     IOT[Capteurs IoT]

#     USERS --> ALB[Application Load Balancer HTTPS]
#     IOT --> APIGW[API Gateway]

#     APIGW --> LAMBDA[Lambda ingestion IoT]
#     ALB --> ECS[ECS Fargate FastAPI / Streamlit]

#     subgraph PROD[solarmboa-prod-vpc]
#         ECS --> REDIS[ElastiCache Redis]
#         ECS --> DOCDB[DocumentDB / MongoDB Atlas]
#         ECS --> NEO4J[Neo4j privé sur EC2/ECS]
#         ECS --> INFLUX[InfluxDB privé sur ECS/EC2]
#         ECS --> CASS[Cassandra sur EC2/EKS]

#         LAMBDA --> SQS[SQS Buffer]
#         SQS --> ETL[ECS Task / Glue Job]
#         ETL --> S3B[S3 Bronze]
#         S3B --> S3S[S3 Silver]
#         S3S --> S3G[S3 Gold]
#         S3G --> ATHENA[Athena / Redshift Spectrum]
#         ATHENA --> BI[QuickSight]
#     end

#     ADMIN[Admin DevOps] --> SSM[SSM Session Manager]
#     SSM --> PROD    


    
#     '''
# )

# st.info('''    Règles de sécurité
# Aucune base NoSQL exposée publiquement.
# Accès admin via AWS Systems Manager, pas SSH public.
# Buckets S3 privés avec Block Public Access activé.
# API publique uniquement via API Gateway ou ALB HTTPS.
# Les services data restent en private subnets.
# Secrets stockés dans AWS Secrets Manager. ''')


from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# Configuration générale
# ============================================================

st.set_page_config(
    page_title="SolarMboa Dashboard",
    page_icon="☀️",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"


# ============================================================
# Chargement des données
# ============================================================

@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    path = WAREHOUSE_DIR / f"{table_name}.csv"

    if not path.exists():
        st.error(f"Table manquante : {path}")
        return pd.DataFrame()

    return pd.read_csv(path)


dim_region = load_table("dim_region")
dim_date = load_table("dim_date")
dim_installation = load_table("dim_installation")
dim_distributor = load_table("dim_distributor")
dim_technician = load_table("dim_technician")
dim_contract_plan = load_table("dim_contract_plan")

fact_telemetry_daily = load_table("fact_telemetry_daily")
fact_payments = load_table("fact_payments")
fact_sales_network = load_table("fact_sales_network")


# ============================================================
# Fonctions de préparation
# ============================================================

def prepare_payments():
    if fact_payments.empty or dim_installation.empty or dim_region.empty:
        return pd.DataFrame()

    df = fact_payments.merge(
        dim_installation[["installation_key", "region_key", "client_type", "contract_plan"]],
        on="installation_key",
        how="left",
    )

    df = df.merge(
        dim_region[["region_key", "region_name"]],
        on="region_key",
        how="left",
    )

    if "date_key" in df.columns and not dim_date.empty:
        df = df.merge(
            dim_date[["date_key", "full_date", "month", "year"]],
            on="date_key",
            how="left",
        )

        df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")

    return df


def prepare_telemetry():
    if fact_telemetry_daily.empty or dim_installation.empty or dim_region.empty:
        return pd.DataFrame()

    df = fact_telemetry_daily.merge(
        dim_installation[["installation_key", "installation_id", "region_key", "client_type", "status", "contract_plan"]],
        on="installation_key",
        how="left",
    )

    df = df.merge(
        dim_region[["region_key", "region_name"]],
        on="region_key",
        how="left",
    )

    if "date_key" in df.columns and not dim_date.empty:
        df = df.merge(
            dim_date[["date_key", "full_date", "month", "year"]],
            on="date_key",
            how="left",
        )

        df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")

    return df


def prepare_sales_network():
    if fact_sales_network.empty:
        return pd.DataFrame()

    df = fact_sales_network.copy()

    if not dim_distributor.empty and "distributor_key" in df.columns:
        df = df.merge(
            dim_distributor[["distributor_key", "distributor_name"]],
            on="distributor_key",
            how="left",
        )

    if not dim_technician.empty and "technician_key" in df.columns:
        df = df.merge(
            dim_technician[["technician_key", "technician_name"]],
            on="technician_key",
            how="left",
        )

    return df



payments = prepare_payments()
telemetry = prepare_telemetry()
sales_network = prepare_sales_network()


# ============================================================
# Sidebar filtres
# ============================================================

st.sidebar.title("Search by ")

available_regions = sorted(telemetry["region_name"].dropna().unique()) if not telemetry.empty else []

selected_regions = st.sidebar.multiselect(
    "Regions",
    options=available_regions,
    default=available_regions,
)

available_client_types = sorted(dim_installation["client_type"].dropna().unique()) if not dim_installation.empty else []

selected_client_types = st.sidebar.multiselect(
    "Types clients",
    options=available_client_types,
    default=available_client_types,
)


available_contract= sorted(dim_installation['contract_plan'].dropna().unique()) if not dim_installation.empty else []

selected_contract = st.sidebar.multiselect(
    "Types contract",
    options = available_contract,
    default=available_contract
)

if not telemetry.empty:
    telemetry_filtered = telemetry[
        telemetry["region_name"].isin(selected_regions)
        & telemetry["client_type"].isin(selected_client_types)
        & telemetry["contract_plan"].isin(selected_contract)
    ]
else:
    telemetry_filtered = telemetry



if not payments.empty:
    payments_filtered = payments[
        payments["region_name"].isin(selected_regions)
        & payments["client_type"].isin(selected_client_types)
        & payments['contract_plan'].isin(selected_contract)
    ]
else:
    payments_filtered = payments


# ============================================================
# Titre
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1 class="title">SolarMboa - Dasboard analytique</h1>
        <p class="subtitle">
            Construction d'une infrastructure de données d'une stratup solaire camerounaise en plein evolution 
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# KPIs principaux
# ============================================================

col1, col2, col3, col4 = st.columns(4)

total_installations = dim_installation["installation_id"].nunique() if not dim_installation.empty else 0

active_installations = (
    dim_installation[dim_installation["status"] == "active"]["installation_id"].nunique()
    if not dim_installation.empty and "status" in dim_installation.columns
    else 0
)

total_revenue = (
    payments_filtered["amount_xaf"].sum()
    if not payments_filtered.empty and "amount_xaf" in payments_filtered.columns
    else 0
)

total_alerts = (
    telemetry_filtered["alert_count"].sum()
    if not telemetry_filtered.empty and "alert_count" in telemetry_filtered.columns
    else 0
)

col1.metric("Installations totales", f"{total_installations:,}"),
col2.metric("Installations actives", f"{active_installations:,}")
col3.metric("Revenus XAF", f"{total_revenue:,.0f}")
col4.metric("Alertes détectées", f"{total_alerts:,.0f}")

col1, col2, col3  = st.columns(3)



with col1:
    if not payments_filtered.empty and "contract_plan" in payments_filtered.columns:
        revenue_plan = (
            payments_filtered.groupby("contract_plan", as_index=False)
            .agg(total_revenue_xaf=("amount_xaf", "sum"), installations=('installation_id', 'nunique'))
            .sort_values("total_revenue_xaf", ascending=False)
        )

        fig = px.pie(
            revenue_plan,
            names="contract_plan",
            values="total_revenue_xaf",
            title="Répartition des revenus par plan tarifaire",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée de plan tarifaire disponible.")
        
    
with col2:
    if not dim_installation.empty:
        status_count = (
            dim_installation.groupby("status", as_index=False)
            .agg(installations=("installation_id", "nunique"))
            .sort_values("installations", ascending=False)
        )

        fig = px.pie(
            status_count,
            names="status",
            values="installations",
            title="Répartition des installations par statut",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée d'installation disponible.")        
        

with col3:

#Meilleurs moyen de paiement
    contract = (
    payments_filtered.groupby('contract_plan', as_index=False)
    .agg(installations=("installation_id", "nunique"))
    )

    fig = px.pie(
        contract,
        names="contract_plan",
        values= "installations",
        title='Repartition des plans par installations',  
    )

    st.plotly_chart(fig, use_container_width=True)



# ============================================================
# Visualisation 1 : Evolution des installations et de la productivité 
# ============================================================


col1, col2 = st.columns(2)

with col1:
    prod_daily = (
        telemetry_filtered.groupby("full_date", as_index=False)
        .agg(consumption = ("avg_consumption_w", 'mean'))
        .dropna()
        .sort_values("full_date")
    )
    
    fig = px.line(
        prod_daily,
        x='full_date',
        y='consumption',
        title='Consummation moyenne par jour',
        labels={
            'full_date':'Date',
            'consumption': 'Consummation moyenne (W)',
        }       
      )
    
    st.plotly_chart(fig, use_container_width=True)
    
with col2:
    inst_daily = (
        telemetry_filtered.groupby("full_date", as_index=True)
        .agg(inst=("installation_key", "nunique"))        
    )
    
    fig = px.line (
        inst_daily,
        x="inst",
        y="inst",
        title="Nombre d'installation par jour",
        labels={
            'full_date': 'Date',
            'inst':'Nombre installation'
        }
    )
 
    st.plotly_chart(fig, use_container_width=True)
    
    
# ============================================================
# Visualisation 1 : production par région
# ============================================================
    
col1, col2 = st.columns(2)

with col1:
    prod_region = (
        telemetry_filtered.groupby("region_name", as_index=False)
        .agg(avg_solar_output_w=("avg_solar_output_w", "mean"))
        .sort_values("avg_solar_output_w", ascending=False)
    )   
    
    fig = px.line(
        prod_region,
        x="region_name",
        y="avg_solar_output_w",
        title="Production solaire moyenne par région",
        labels={
            "region_name": "Région",
            "avg_solar_output_w": "Production moyenne (W)",
        },
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
with col2:
    revenue_region = (
        payments_filtered.groupby("region_name", as_index=False)
        .agg(total=("amount_xaf", "sum"))
    )    
    # st.dataframe(revenue_region)
    
    fig = px.pie(
        revenue_region,
        names="region_name",
        values="total",
        title='Revenus totaux par region',
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
# ============================================================
# Visualisation 1 : production solaire par région
# ============================================================

st.subheader("1. Production solaire moyenne par région")

if not telemetry_filtered.empty:
    prod_region = (
        telemetry_filtered.groupby("region_name", as_index=False)
        .agg(avg_solar_output_w=("avg_solar_output_w", "mean"))
        .sort_values("avg_solar_output_w", ascending=False)
    )

    fig = px.bar(
        prod_region,
        x="region_name",
        y="avg_solar_output_w",
        title="Production solaire moyenne par région",
        labels={
            "region_name": "Région",
            "avg_solar_output_w": "Production moyenne (W)",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée de télémétrie disponible.")


# ============================================================
# Visualisation 2 : évolution de la production solaire
# ============================================================

st.subheader("2. Évolution de la production solaire")

if not telemetry_filtered.empty and "full_date" in telemetry_filtered.columns:
    prod_daily = (
        telemetry_filtered.groupby("full_date", as_index=False)
        .agg(avg_solar_output_w=("avg_solar_output_w", "mean"))
        .dropna()
        .sort_values("full_date")
    )

    fig = px.line(
        prod_daily,
        x="full_date",
        y="avg_solar_output_w",
        title="Production solaire moyenne par jour",
        labels={
            "full_date": "Date",
            "avg_solar_output_w": "Production moyenne (W)",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Impossible de construire l'évolution temporelle.")


# ============================================================
# Visualisation 3 : revenus par région
# ============================================================

st.subheader("3. Revenus par région")

if not payments_filtered.empty:
    revenue_region = (
        payments_filtered.groupby("region_name", as_index=False)
        .agg(total_revenue_xaf=("amount_xaf", "sum"))
        .sort_values("total_revenue_xaf", ascending=False)
    )

    fig = px.bar(
        revenue_region,
        x="region_name",
        y="total_revenue_xaf",
        title="Revenus totaux par région",
        labels={
            "region_name": "Région",
            "total_revenue_xaf": "Revenus XAF",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée de paiement disponible.")


# ============================================================
# Visualisation 4 : revenus par plan tarifaire
# ============================================================

st.subheader("4. Revenus par plan tarifaire")

# if not payments_filtered.empty and "contract_plan" in payments_filtered.columns:
#     revenue_plan = (
#         payments_filtered.groupby("contract_plan", as_index=False)
#         .agg(total_revenue_xaf=("amount_xaf", "sum"))
#         .sort_values("total_revenue_xaf", ascending=False)
#     )

#     fig = px.pie(
#         revenue_plan,
#         names="contract_plan",
#         values="total_revenue_xaf",
#         title="Répartition des revenus par plan tarifaire",
#     )

#     st.plotly_chart(fig, use_container_width=True)
# else:
#     st.warning("Aucune donnée de plan tarifaire disponible.")


# ============================================================
# Visualisation 5 : alertes par région
# ============================================================

st.subheader("5. Alertes par région")

if not telemetry_filtered.empty:
    alerts_region = (
        telemetry_filtered.groupby("region_name", as_index=False)
        .agg(total_alerts=("alert_count", "sum"))
        .sort_values("total_alerts", ascending=False)
    )

    fig = px.bar(
        alerts_region,
        x="region_name",
        y="total_alerts",
        title="Nombre total d'alertes par région",
        labels={
            "region_name": "Région",
            "total_alerts": "Nombre d'alertes",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée d'alertes disponible.")


# ============================================================
# Visualisation 6 : état du parc
# ============================================================

st.subheader("6. État du parc d'installations")

# if not dim_installation.empty:
#     status_count = (
#         dim_installation.groupby("status", as_index=False)
#         .agg(installations=("installation_id", "nunique"))
#         .sort_values("installations", ascending=False)
#     )

#     fig = px.pie(
#         status_count,
#         names="status",
#         values="installations",
#         title="Répartition des installations par statut",
#     )

#     st.plotly_chart(fig, use_container_width=True)
# else:
#     st.warning("Aucune donnée d'installation disponible.")


# ============================================================
# Visualisation 7 : top distributeurs
# ============================================================

st.subheader("7. Top distributeurs par volume de relations")

if not sales_network.empty and "distributor_name" in sales_network.columns:
    top_distributors = (
        sales_network.dropna(subset=["distributor_name"])
        .groupby("distributor_name", as_index=False)
        .agg(total_relations=("sales_network_key", "count"))
        .sort_values("total_relations", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_distributors,
        x="total_relations",
        y="distributor_name",
        orientation="h",
        title="Top 10 distributeurs par relations réseau",
        labels={
            "total_relations": "Nombre de relations",
            "distributor_name": "Distributeur",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée distributeur disponible.")


# ============================================================
# Tables de contrôle
# ============================================================

with st.expander("Voir les tables du Data Warehouse"):
    st.write("dim_installation")
    st.dataframe(dim_installation.head(100), use_container_width=True)

    st.write("fact_telemetry_daily")
    st.dataframe(fact_telemetry_daily.head(100), use_container_width=True)

    st.write("fact_payments")
    st.dataframe(fact_payments.head(100), use_container_width=True)
    
    st.write("dim_contract_plan")
    st.dataframe(dim_contract_plan.head(100), use_container_width=True)
    
st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
    }

    .hero {
        padding: 2.5rem;
        border-radius: 24px;
        background: linear-gradient(100deg, #0f172a 0%, #14532d 50%, #facc15 140%);
        color: white;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: 1.2rem;
        color: #e5e7eb;
    }

    .card {
        padding: 1.4rem;
        border-radius: 18px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
        height: 100%;
    }

    .card h3 {
        margin-bottom: 0.5rem;
        color: #0f172a;
    }

    .card p {
        color: #475569;
        font-size: 0.95rem;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #dcfce7;
        color: #166534;
        margin-bottom: 0.8rem;
    }

    .badge-wip {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #fef9c3;
        color: #854d0e;
        margin-bottom: 0.8rem;
    }
    
    div{
        margin:0.1rem 0;
    }
    
    
    .subtitle {
        font-size: 0.5rem;
        font-weight: 700;
        opacity:70%;
    }
    
    .title {
        opacity:95%;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)    