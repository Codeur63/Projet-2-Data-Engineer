# ARCHITECTURE DECISION RECORD
## sujet : Stockage massive de la télemétrie
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SOLARMBOA envoye environ 120960 données réel par jour qui sont envoyées et nous avons besoin des les garders sans toutes fois interferes sur les performances de la BD ainsi que sur la replication des données, La disponibilité est réquise au cas ou des noeuds pourrais tomber.

## DÉCISION

## POSITIONNEMENT CAP
Nous utilisons cassandra 4.1 sur un cluster avec 3 noeuds pour la replication parfaite des données. En cas de noeuds qui tombe un autre noeud pourrais prendre le relais et toujours écrit les données qui seront recopier par les autres noeuds quand il seras retablis. La Disponibilité est non-négociable: Les données qui ne pourront pas etre ecrite sont des pertes de performances en tant réel.    

## ALTERNATIVES CONSIDÉRÉES
MySQL : Supporte les données mais avec plus de 1M de données pas jour il ne pourrais pas supporter le rythme. 

## CONSÉQUENCES
Négatives : Écrire les tables en fonction des rêquetes que l'on pourrait vouloir. Peut avoir des interminables tables, ainsi que que Eviter ALLOW FIlTERING en production