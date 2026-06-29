import streamlit as st

st.set_page_config(
    page_title="SolarMboa Data Platform",
    page_icon="☀️",
    layout="wide",
)

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

st.markdown(
    """
    <div class="hero">
        <h1 class="title">☀️ SolarMboa Data Platform</h1>
        <p class="subtitle">
            Construction d'une infrastructure de données d'une stratup solaire camerounaise en plein evolution 
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div> 
        <h2> Implémentation de 5 bases de données NoSQL pour l'architecture Data de la Platform </h2>
    </div> 
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

col4, col5 = st.columns(2) 

with col1:
    st.markdown(
        """
        <div class="card">
            <span class="badge">Redis terminé</span>
            <h3>⚡ Cache temps réel</h3>
            <p>
                Redis accélère l'accès aux sessions capteurs, gère les TTL,
                la stratégie LRU, les compteurs actifs et les leaderboards.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <span class="badge">Termine</span>
            <h3>🍃 MongoDB</h3>
            <p>
                MongoDB stockera les profils enrichis des installations :
                équipements, contrat, client, localisation et historique qui peuvent etre différent entre capteurs
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <span class="badge">Terminer </span>
            <h3>📈 Cassandra</h3>
            <p>
                Cassandra seras dedié à stocker des données :
                ingestion massive, métriques solaires, regions et capteurs quasi temps réel.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
with col4:
    st.markdown(
        """
        <div class="card">
            <span class="badge">Terminer </span>
            <h3>📈 InfluxDB</h3>
            <p>
                InfluxDB seront dédiées aux séries temporelles :
                ingestion massive,métriques solaires, et alert code temps réel.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    
with col5:
    st.markdown(
        """
        <div class="card">
            <span class="badge">Terminer </span>
            <h3>📈  Neo4J </h3>
            <p>
                Neo4j seras dédiées aux relation entre les tables :
                Récupération rapide des liens entre les tables sous forme de graph ou de table.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )    
        

st.markdown("## Architecture cible pour solarmboa")

st.markdown(
    """
```text
Capteurs IoT
   ↓
API d'ingestion
   ↓
Redis ───────────────► Cache sessions / compteurs actifs / leaderboard
   ↓
MongoDB ─────────────► Profils installations
   ↓
Cassandra ─────────────► Ingestion Massive des données dans un cluster
   ↓
InfluxDB ─────────────► Séries temporelles et métriques temps réel    
   ↓
Neo4j ─────────────► Relation entre les tables, Graph
  ↓
AWS Finops
   ↓
Data Lake AWS S3
   ↓
Data Warehouse
   ↓
BI / Dashboard Streamlit

""")

st.info("Developper le menu latéral pour ouvrir les pages de simulations des BD NoSQL.")

st.markdown(
    '''
    # SolarMboa — Architecture réseau GCP

## Objectif

Concevoir une infrastructure réseau sécurisée avec deux environnements séparés :

- `solarmboa-prod-vpc`
- `solarmboa-staging-vpc`

Chaque environnement possède ses propres subnets, règles firewall minimales et accès contrôlés.

## Diagramme réseau

```mermaid
flowchart TD

    USERS[Utilisateurs / Dashboard]
    IOT[Capteurs IoT]
    
    USERS --> LB[HTTPS Load Balancer]
    IOT --> LB

    LB --> CR[Cloud Run API Ingestion]

    subgraph PROD[solarmboa-prod-vpc]
        CR --> PUBSUB[Pub/Sub]
        PUBSUB --> DATAFLOW[Dataflow / Cloud Run Jobs]
        DATAFLOW --> GCS[GCS Bronze / Silver / Gold]
        GCS --> BQ[BigQuery]
        
        CR --> REDIS[Memorystore Redis]
        CR --> MONGO[MongoDB Atlas / VM privée]
        CR --> INFLUX[InfluxDB privé]
        CR --> NEO4J[Neo4j privé]
        CR --> CASS[Cassandra / Bigtable alternative]
    end

    subgraph STAGING[solarmboa-staging-vpc]
        CR_STG[Cloud Run Staging]
        GCS_STG[GCS staging]
        BQ_STG[BigQuery staging]
    end

    ADMIN[Admin / DevOps] --> IAP[IAP / Bastion sécurisé]
    IAP --> PROD
    IAP --> STAGING
```

# SolarMboa — Architecture réseau AWS

## Objectif

Déployer SolarMboa sur AWS avec deux environnements isolés :

- `solarmboa-prod-vpc`
- `solarmboa-staging-vpc`

Chaque environnement contient des subnets publics uniquement pour l’entrée contrôlée, et des subnets privés pour les services applicatifs et data.

## Diagramme

```mermaid
flowchart TD

    USERS[Utilisateurs / Dashboard]
    IOT[Capteurs IoT]

    USERS --> ALB[Application Load Balancer HTTPS]
    IOT --> APIGW[API Gateway]

    APIGW --> LAMBDA[Lambda ingestion IoT]
    ALB --> ECS[ECS Fargate FastAPI / Streamlit]

    subgraph PROD[solarmboa-prod-vpc]
        ECS --> REDIS[ElastiCache Redis]
        ECS --> DOCDB[DocumentDB / MongoDB Atlas]
        ECS --> NEO4J[Neo4j privé sur EC2/ECS]
        ECS --> INFLUX[InfluxDB privé sur ECS/EC2]
        ECS --> CASS[Cassandra sur EC2/EKS]

        LAMBDA --> SQS[SQS Buffer]
        SQS --> ETL[ECS Task / Glue Job]
        ETL --> S3B[S3 Bronze]
        S3B --> S3S[S3 Silver]
        S3S --> S3G[S3 Gold]
        S3G --> ATHENA[Athena / Redshift Spectrum]
        ATHENA --> BI[QuickSight]
    end

    ADMIN[Admin DevOps] --> SSM[SSM Session Manager]
    SSM --> PROD    


    
    '''
)

st.info('''    Règles de sécurité
Aucune base NoSQL exposée publiquement.
Accès admin via AWS Systems Manager, pas SSH public.
Buckets S3 privés avec Block Public Access activé.
API publique uniquement via API Gateway ou ALB HTTPS.
Les services data restent en private subnets.
Secrets stockés dans AWS Secrets Manager. ''')