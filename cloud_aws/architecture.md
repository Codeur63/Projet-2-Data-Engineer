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

    Règles de sécurité
Aucune base NoSQL exposée publiquement.
Accès admin via AWS Systems Manager, pas SSH public.
Buckets S3 privés avec Block Public Access activé.
API publique uniquement via API Gateway ou ALB HTTPS.
Les services data restent en private subnets.
Secrets stockés dans AWS Secrets Manager. 