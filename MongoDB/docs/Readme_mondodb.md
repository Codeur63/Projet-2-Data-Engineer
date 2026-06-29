# ARCHITECTURE DECISION RECORD
## sujet : Stockage des profils d'installation clients SolarMboa
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SolarMboa gère 4 800 installations solaires réparties en 4 types de clients (residential, sme, health_center, school) avec des champs métier hétérogènes par type. Le schéma évolue fréquemment (nouveau type de contrat, nouveaux équipements, nouveaux indicateurs de performance). Les requêtes incluent des filtres géospatiaux (GPS), des agrégations complexes par région/type/plan, et des jointures avec les paiements. La cohérence est requise pour éviter des erreurs de facturation.

## DÉCISION
Nous utilisons MongoDB 7.2 en Replica Set (1 Primary + 2 Secondaries) avec writeConcern: majority pour les profils d'installation. La collection 'installations' contient des documents polymorphes discriminés par le champ 'client_type'. Un index 2dsphere couvre les requêtes géospatiales. La validation JSON Schema impose les champs obligatoires et les valeurs canoniques.

## POSITIONNEMENT CAP
MongoDB Replica Set avec writeConcern: majority est un système CP (Cohérence + Tolérance au Partitionnement). En cas de partition réseau, MongoDB refuse d'écrire s'il ne peut pas confirmer la réplication sur la majorité des nœuds. Pour les profils d'installation (données de référence pour la facturation), la cohérence forte est non-négociable : un plan tarifaire incorrect peut générer une facture erronée avec impact client immédiat et risque légal.

## ALTERNATIVES CONSIDÉRÉES
PostgreSQL avec JSONB : Supporte les documents JSON dans des colonnes JSONB avec des index GIN. Très performant mais chaque nouveau champ métier nécessite une migration DDL. Le schéma
des 4 types de clients forcerait soit une table surchargée de colonnes NULL soit une architecture EAV (Entity-Attribute-Value) inextricable. Rejeté. 

Firestore (GCP) : Base documentaire managée parfaitement intégrée avec notre infrastructure cloud (BigQuery, Cloud Run). Limitations rédhibitoires : pas de $group natif, pas de $lookup, coût à l'opération (estimé 3× plus cher que MongoDB self-managed à notre volume). Rejeté.

Elasticsearch : Excellent pour la recherche full-text et les agrégations analytiques, mais pas conçu comme base opérationnelle primaire. Pas de transactions multi-documents, cohérence éventuelle par défaut, model de données dénormalisé forcé. Pourrait être utilisé en complément comme moteur de recherche. Rejeté comme base principale.

## CONSÉQUENCES
Positives : Schéma flexible sans migration DDL pour les nouveaux types de clients, index 2dsphere natif pour les opérations terrain, pipelines d'agrégation expressifs pour les dashboards, scalabilité horizontale via sharding si volume > 1M installations, support des transactions ACID pour les opérations critiques (changement de distributeur).

Négatives : Limite de 16 Mo par document (ne jamais y stocker la télémétrie), jointures moins performantes qu'en SQL (utiliser $lookup avec parcimonie), complexité opérationnelle du Replica Set (monitoring, failover, backup), license SSPL pour usage cloud commercial.

Risques mitigés : Validation JSON Schema sur les champs critiques + tests Pytest sur le repository + tests de cohérence croisés entre MongoDB et BigQuery lors de l'export vers la couche analytique (pipeline dbt hebdomadaire).



