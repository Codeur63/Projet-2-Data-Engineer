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
            <span class="badge-wip">À construire</span>
            <h3>🍃 MongoDB</h3>
            <p>
                MongoDB stockera les profils enrichis des installations :
                équipements, contrat, client, localisation et historique.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <span class="badge-wip">À construire</span>
            <h3>📈 Cassandra / InfluxDB</h3>
            <p>
                Cassandra et InfluxDB seront dédiées aux séries temporelles :
                ingestion massive et métriques solaires quasi temps réel.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
with col4:
    st.markdown(
        """
        <div class="card">
            <span class="badge-wip">À construire</span>
            <h3>📈 Cassandra / InfluxDB</h3>
            <p>
                Cassandra et InfluxDB seront dédiées aux séries temporelles :
                ingestion massive et métriques solaires quasi temps réel.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    
with col5:
    st.markdown(
        """
        <div class="card">
            <span class="badge-wip">À construire</span>
            <h3>📈 Cassandra / InfluxDB</h3>
            <p>
                Cassandra et InfluxDB seront dédiées aux séries temporelles :
                ingestion massive et métriques solaires quasi temps réel.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )    
        

st.markdown("## Architecture cible")

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
Cassandra / InfluxDB ─► Séries temporelles et métriques temps réel
   ↓
Neo4j ─────────────► Graph
   ↓
Data Lake AWS S3
   ↓
Data Warehouse
   ↓
BI / Dashboard


""")

st.info("Utilise le menu latéral pour ouvrir la page Redis et lancer une simulation de télémétrie.")