# ARCHITECTURE DECISION RECORD
## sujet : Stockage massive de la télemétrie
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SolarMboa envoie environ 120 960 données par jour et nous devons les conserver sans impacter fortement les performances de la base ni la réplication. Les données sont écrites en continu et doivent rester disponibles même si certains nœuds tombent. La disponibilité est critique, car toute perte d’écriture en temps réel représente une perte de données métier.

## DÉCISION
Nous utilisons Apache Cassandra 4.1 sur un cluster de 3 nœuds pour stocker la télémétrie. Les écritures sont réparties sur plusieurs réplicas afin de garantir la continuité de service, et le cluster permet de continuer à recevoir des écritures même si un nœud devient indisponible. Les lectures et écritures seront modélisées selon les patterns d’accès réels de l’application, avec des requêtes directes sur les clés de partition pour éviter les scans coûteux.+1

## POSITIONNEMENT CAP
Cassandra est un système AP dans notre contexte : nous privilégions la disponibilité et la tolérance au partitionnement plutôt qu’une cohérence forte immédiate. En cas de panne réseau ou de perte temporaire d’un nœud, le système continue de fonctionner et les données sont répliquées puis réconciliées ensuite. Pour la télémétrie, ce compromis est acceptable car l’objectif principal est de ne pas interrompre la collecte en temps réel.

## ALTERNATIVES CONSIDÉRÉES
MySQL : base relationnelle fiable, mais moins adaptée à un flux continu de télémétrie à fort volume. Le modèle relationnel devient moins performant lorsque les écritures sont très fréquentes et que les volumes augmentent rapidement.

InfluxDB : très adaptée aux séries temporelles, mais dans ce cas Cassandra a été retenue pour sa capacité de distribution, sa haute disponibilité et sa flexibilité de modélisation sur un cluster de production. 

## CONSÉQUENCES
Positives : haute disponibilité, scalabilité horizontale, réplication des données, tolérance aux pannes de nœuds, et bonnes performances pour les écritures massives. Cassandra est particulièrement adaptée aux charges distribuées et aux données qui doivent rester accessibles même en cas d’incident.

Négatives : la modélisation doit être pensée à partir des requêtes, ce qui oblige à créer des tables orientées usage. Les requêtes exploratoires sont coûteuses, et il faut éviter ALLOW FILTERING en production car cela peut provoquer des scans distribués et des problèmes de performance.

Risques mitigés : définir les partitions en fonction des requêtes métier, limiter les requêtes non ciblées, surveiller la santé du cluster, et mettre en place des politiques de réplication et de réparation adaptées. Il faut aussi tester les patterns d’accès avant la mise en production.