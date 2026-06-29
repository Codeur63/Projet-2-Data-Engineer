# ARCHITECTURE DECISION RECORD
## sujet : Stockage des rélations entre les CSV
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
Solarmboa gère 4800 installations solaires dont des distrubuteurs pour vendre les installations, qui emploies des techniciens pour maintenir les installations suivant, qui sont dans des régions précises. Nous devons être capables de faire des requêtes rapide grâce a des jointures pour trouver certains correlations entre plusieurs tables. La cohérence est réquise pour éviter des erreurs d'installation     

## DÉCISION
Nous utilisons Neo4J 5.20-community pour pouvoir realiser des relations ou connexion entre nos différentes tables. Le dataset network_graph.csv est notre dataset de reference relationnel que nous allons importer dans al BD pour les relations, tout aussi en utilisant network_node_distributor.csv et network_node_technicians.csv pour les inclures.

## POSITIONNEMENT CAP
Neo4J est un système CP (Cohérence + Tolérance au Partitionnement). En cas de mauvaise cohérence entre les rélations de nos données ont risque de ne pas avoir le résultat souhaité, il faut donc privilegiés la cohérence et la Tolérance.   

## ALTERNATIVES CONSIDÉRÉES 
MySQL avec csv: Supporte les csv mais chaque requete seront des interminables jointures et rendrons les requetes beaucoup plus lente.

## CONSÉQUENCES
Positives : Intégration facile des rélations, requêtes plus simple et plus rapide, scalabilité vertical.
Négatives : 
Risques mitigés :  