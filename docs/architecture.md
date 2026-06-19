# Architecture globale SolarMboa Data Platform

```mermaid
flowchart TD

    A[Capteurs IoT SolarMboa] --> B[API / Ingestion FastAPI]

    B --> R[Redis Cache]
    B --> M[MongoDB]
    B --> I[InfluxDB]
    B --> C[Cassandra]
    B --> N[Neo4j]

    R --> R1[Sessions capteurs]
    R --> R2[Cache MongoDB]
    R --> R3[Leaderboard temps réel]
    R --> R4[TTL + LRU]

    M --> M1[Profils installations]
    M --> M2[Contrats]
    M --> M3[Maintenance]
    M --> M4[Localisation GPS]

    I --> I1[Séries temporelles récentes]
    I --> I2[Production solaire]
    I --> I3[Batterie]
    I --> I4[Consommation]
    I --> I5[Alertes]

    C --> C1[Historique massif IoT]
    C --> C2[Par capteur/jour]
    C --> C3[Par région/jour]
    C --> C4[Alertes long terme]

    N --> N1[Graphe opérationnel]
    N --> N2[Distributeurs]
    N --> N3[Techniciens]
    N --> N4[Installations]
    N --> N5[Relations SOLD / MAINTAINS / EMPLOYS]

    R --> D[Dashboard Streamlit]
    M --> D
    I --> D
    C --> D
    N --> D

    M <--> R
    B --> S[AWS S3 Data Lake - prochaine étape]
    S --> W[Data Warehouse / BI]