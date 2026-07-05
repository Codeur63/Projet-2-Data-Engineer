# SolarMboa Data Warehouse

## 1. Objectif

Le Data Warehouse SolarMboa a pour objectif de centraliser les données provenant des différentes bases opérationnelles (MongoDB, InfluxDB, Cassandra, Neo4j et fichiers CSV) afin de produire des indicateurs métier fiables pour les équipes de direction, les dashboards BI et les analyses historiques.

Contrairement aux bases opérationnelles, le Data Warehouse est optimisé pour la lecture, l'analyse et l'agrégation de grands volumes de données.

Le modèle retenu est un **schéma en étoile (Star Schema)**, permettant d'améliorer les performances analytiques et de simplifier la création de rapports.

---

# 2. Sources de données

Le Data Warehouse est alimenté par plusieurs systèmes spécialisés.

| Source       | Type        | Contenu                                          |
| ------------ | ----------- | ------------------------------------------------ |
| MongoDB      | Document    | Installations, clients, contrats                 |
| InfluxDB     | Time Series | Production solaire, consommation, batterie       |
| Cassandra    | Wide Column | Historique IoT                                   |
| Neo4j        | Graph       | Réseau distributeurs, techniciens, installations |
| Payments CSV | Fichier     | Historique des paiements                         |

---

# 3. Architecture décisionnelle

Le Data Warehouse suit une architecture en étoile.

```text
                Dimensions

        Date
          │
Installation ─────┐
Client            │
Region            │
Distributor       │
Technician        │
Contract Plan     │
Alert             │
                  │
                  ▼

          Tables de faits
```

Chaque table de faits contient des mesures numériques tandis que les dimensions décrivent le contexte métier.

---

# 4. Tables de dimensions

## dim_date

Décrit toutes les informations temporelles utilisées dans les analyses.

Exemples :

* Jour
* Mois
* Trimestre
* Année
* Jour de semaine

Cette dimension évite de recalculer ces informations dans chaque requête.

---

## dim_installation

Décrit chaque installation photovoltaïque.

Informations principales :

* Installation
* Ville
* Région
* Statut
* Type de client
* Date d'installation

---

## dim_client

Décrit les propriétaires des installations.

Informations :

* Nom
* Type de client
* Segment
* Région

---

## dim_region

Liste des régions couvertes par SolarMboa.

Exemple :

* Centre
* Littoral
* Ouest
* Nord
* Est

Cette dimension permettra les analyses géographiques.

---

## dim_distributor

Informations sur les distributeurs.

Exemples :

* Nom
* Région
* Ancienneté

---

## dim_technician

Informations concernant les techniciens.

Exemples :

* Nom
* Région
* Certification

---

## dim_contract_plan

Décrit les différents abonnements.

Exemples :

* Standard
* Premium
* Basic
* Custom

---

## dim_alert

Répertorie les différents codes d'alerte remontés par les capteurs.

Exemples :

* OVERCURRENT
* FAULT_02
* OVR_V
* AUCUNE

---

# 5. Tables de faits

Les tables de faits stockent les événements mesurables.

## fact_telemetry_daily

Grain :

Une ligne par installation et par jour.

Mesures :

* Production solaire
* Consommation
* Niveau batterie
* Nombre d'alertes

Cette table servira principalement aux dashboards énergétiques.

---

## fact_payments

Grain :

Une ligne par paiement.

Mesures :

* Montant
* TVA
* Remise
* Solde

Utilisée pour les analyses financières.

---


## fact_sales_network

Grain :

Une ligne par relation commerciale.

Mesures :

* Nombre d'installations vendues
* Nombre d'interventions
* Chiffre d'affaires associé

Cette table exploite les relations modélisées dans Neo4j.

---

# 6. Flux de données

Le processus d'alimentation suit les étapes suivantes.

```text
MongoDB
InfluxDB
Cassandra
Neo4j
CSV

        │

        ▼

ETL 

        │

Transformation

        │

Data Warehouse

        │

Power BI
Streamlit
Dashboards CTO
```

---

# 7. Choix du modèle en étoile

Le schéma en étoile a été retenu pour plusieurs raisons.

* simplicité des requêtes SQL ;
* bonnes performances sur les agrégations ;
* facilité de compréhension par les analystes métier ;
* compatibilité avec les outils BI modernes ;
* évolutivité pour l'ajout de nouveaux indicateurs.

Ce modèle constitue le socle analytique de SolarMboa et complète les bases NoSQL orientées opérationnelles.
