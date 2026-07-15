# SolarMboa Data & AI Engineering Platform

## 1. Présentation du projet

SolarMboa Technologies est une startup solaire camerounaise qui souhaite industrialiser la collecte, le stockage, le traitement et l’analyse de données issues de ses installations solaires connectées.

Ce projet met en place une architecture Data complète autour de plusieurs briques :

- bases NoSQL spécialisées ;
- API REST d’ingestion avec FastAPI ;
- Data Lake AWS S3 en architecture bronze / silver / gold ;
- Data Warehouse local en schéma étoile ;
- dashboard BI avec Streamlit ;
- scripts de contrôle et de simulation ;
- documentation d’architecture cloud AWS.

L’objectif est de construire une plateforme capable de gérer des données IoT, des installations, des paiements, des distributeurs, des techniciens et des indicateurs métiers utiles pour le pilotage opérationnel.

---

## 2. Objectifs fonctionnels

Le projet couvre les besoins suivants :

- stocker les profils d’installations solaires ;
- ingérer des mesures IoT unitaires ou en batch ;
- structurer les données dans un Data Lake AWS S3 ;
- stocker l’historique de télémétrie ;
- produire des KPI BI dans un dashboard Streamlit ;

---

## 3. Architecture générale

```text
Capteurs IoT 
        ↓
FastAPI REST API
        ↓
Bases NoSQL opérationnelles
 ├── Redis       : cache, dernière mesure, accès rapide
 ├── MongoDB     : installations, contrats, maintenance
 ├── InfluxDB    : séries temporelles temps réel
 ├── Cassandra   : historique long terme de télémétrie
 └── Neo4j       : réseau distributeurs / techniciens / installations 
        ↓
Data Lake AWS S3
 ├── bronze/
 ├── silver/
 └── gold/
        ↓
Data Warehouse 
        ↓
Dashboard Streamlit/ PowerBI
```

---

## 4. Technologies utilisées

### Langage et environnement

- Python 3.11+
- Poetry
- Docker / Docker Compose
- aws 

### Bases de données

- Redis
- MongoDB
- InfluxDB
- Cassandra
- Neo4j

### API

- FastAPI
- Uvicorn
- Pydantic

### Data Engineering

- Pandas
- PyArrow / Parquet
- Boto3
- AWS S3
- AWS Glue
- Redshit / Athena selon accès AWS

### Dashboard

- Streamlit
- Plotly
- Pandas

---

## 5. Données utilisées

Le projet utilise plusieurs sources de données :

```text

data/raw/
├── sensors_telemetry.csv
├── installations.json
├── payments.csv
├── network_graph.csv
├── network_nodes_distributors.csv
└── network_nodes_technicians.csv

```

### Rôle des fichiers

| Fichier | Rôle |
|---|---|
| `sensors_telemetry.csv` | Mesures IoT des capteurs solaires |
| `installations.json` | Profils des installations solaires |
| `payments.csv` | Historique des paiements |
| `network_graph.csv` | Relations réseau |
| `network_nodes_distributors.csv` | Informations distributeurs |
| `network_nodes_technicians.csv` | Informations techniciens |

---

## 6. Installation du projet

### 6.1. Cloner le dépôt

```bash
git clone <URL_DU_REPO>
cd Projet2
```

### 6.2. Installer les dépendances avec Poetry

```bash
poetry install
```

Si certaines dépendances manquent :

```bash
poetry add fastapi uvicorn pydantic-settings pymongo redis influxdb-client cassandra-driver streamlit plotly pandas boto3 pyarrow
```

---

## 7. Configuration des variables d’environnement

Créer un fichier `.env` à partir de `.env.example`.

Exemple :

```env
# API
APP_NAME=SolarMboa Data API
APP_VERSION=1.0.0

# MongoDB
MONGODB_URI=mongodb://solarmboa_app:app_password_2026@localhost:27017/solarmboa?authSource=solarmboa
MONGODB_DATABASE=solarmboa

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=solarmboa_influx_token_2026
INFLUXDB_ORG=solarmboa
INFLUXDB_BUCKET=iot_telemetry

# Cassandra
CASSANDRA_HOSTS=localhost
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=solarmboa

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password_2026

# AWS
AWS_DEFAULT_REGION=eu-east-2
S3_BUCKET=solarmboa-prod-data-lake
```
---

## 8. Lancer les bases NoSQL avec Docker

```bash
docker compose up -d
```

Vérifier que les conteneurs tournent :

```bash
docker ps
```

Les services attendus sont :

```text

MongoDB
Redis
InfluxDB
Cassandra
Neo4j
```

---

## 9. API FastAPI

### 9.1. Lancer l’API

```bash
poetry run uvicorn api.main:app --reload --port 8000
```

Documentation Swagger :

```text
http://localhost:8000/docs
```

Health check :

```text
http://localhost:8000/health
```

### 9.2. Endpoints principaux

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Vérifier l’état de l’API |
| `POST` | `/api/v1/installations` | Créer une installation |
| `GET` | `/api/v1/installations/{installation_id}` | Lire une installation |
| `PATCH` | `/api/v1/installations/{installation_id}/status` | Modifier le statut d’une installation |
| `POST` | `/api/v1/installations/{installation_id}/maintenance` | Ajouter une intervention de maintenance |
| `POST` | `/api/v1/telemetry` | Ingérer une mesure IoT |
| `POST` | `/api/v1/telemetry/batch` | Ingérer plusieurs mesures IoT |
| `GET` | `/api/v1/telemetry/latest/{installation_id}` | Lire la dernière mesure depuis Redis |

---


## 10. Scripts cloud

### Uploader les données bronze

```bash

poetry run python cloud/upload_bronze_to_s3.py
```

### Uploader les tables gold

```bash
poetry run python cloud/upload_gold_to_s3.py
```

### Vérifier la structure S3

```bash
poetry run python cloud/check_s3_datalake.py
```

### Vérifier les couches S3

```bash
poetry run python cloud/check_s3_layers.py

```

---

## 11. AWS Glue et Athena

L’architecture cible prévoit :

```text

S3 bronze
   ↓
AWS Glue Job
   ↓
S3 silver
   ↓
AWS Glue Crawler
   ↓
Glue Data Catalog
   ↓
Athena

```

Les jobs Glue permettent de nettoyer les données bronze et de produire des données silver au format Parquet.

Athena peut ensuite interroger les tables cataloguées avec SQL.

---

## 12. Architecture cloud cible AWS

Certaines bases managées AWS peuvent être limitées selon le type de compte AWS utilisé. Le projet documente donc une architecture cloud cible :

| Local | AWS cible |
|---|---|
| Redis | Amazon ElastiCache for Redis |
| MongoDB | Amazon DocumentDB ou MongoDB Atlas |
| Cassandra | Amazon Keyspaces |
| InfluxDB | Amazon Timestream for InfluxDB |
| Neo4j | Neo4j AuraDB ou Neo4j sur EC2 |
| Data Lake | Amazon S3 |
| Data Warehouse | Amazon Redshift Serverless ou Athena |
| API | ECS Fargate ou Lambda |
| ETL | AWS Glue |
| Monitoring | CloudWatch |

---------



## 13. Limites actuelles

- Le déploiement complet de toutes les bases managées AWS peut être limité par le type de compte AWS utilisé.
- Le dashboard BI est principalement basé sur le Data Warehouse local.
- Le Data Lake S3 est opérationnel, mais l’industrialisation Glue/Athena peut être complétée selon les accès AWS.

---------

## 14. Améliorations futures

- Déployer FastAPI sur ECS Fargate.
- Connecter l’API aux services managés AWS.
- Automatiser les jobs Glue bronze → silver → gold.
- Ajouter Redshift Serverless ou Athena comme moteur analytique principal.
- Ajouter des tests unitaires et tests d’intégration.
- Ajouter CI/CD GitHub Actions.
- Ajouter monitoring CloudWatch.
- Ajouter authentification API.
- Ajouter documentation OpenAPI enrichie.
- Ajouter qualité des données avec Great Expectations ou dbt tests.

---------

## 15. Commandes principales

```bash

# Installer les dépendances
poetry install

# Lancer les bases
docker compose up -d

# Lancer l'API
poetry run uvicorn api.main:app --reload --port 8000

# Lancer le dashboard
poetry run streamlit run dashboard/app.py

# Générer le Data Warehouse
poetry run python datawarehouse/scripts/build_schema.py

# Uploader les données vers S3
poetry run python cloud/upload_bronze_to_s3.py
poetry run python cloud/upload_gold_to_s3.py

# Vérifier S3
poetry run python cloud/check_s3_datalake.py

```

---


