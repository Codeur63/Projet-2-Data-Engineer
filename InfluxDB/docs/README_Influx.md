# ARCHITECTURE DECISION RECORD
## sujet : Stockage massive des données en temps réel 
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SOLARMBOA envoye environ 120960 données réel par jour qui sont envoyées et nous avons besoin d'avoir , de stocker les données qui sont envoyées réel par heures,seconde ou minute. Les données evolue dans le temps et seront supprimer tout les 90 jours. La disponibilité est requise pour éviter les données trucés. 

## DÉCISION
Nous utilisons influxDB 2.7 comme DB pour la télémetrie. Sensors_telemetrie.csv seront les données que nous allons entre dans notre DB, pour la visualition des données d'un capteur au cours de son cycle de vie.

## POSITIONNEMENT CAP
InfluxDB est un système AP. La disponibilité des données est non-négociable.

## ALTERNATIVES CONSIDÉRÉES
MySQL : Supporte les données mais avec plus de 1M de données pas jour il ne pourrais pas supporter le rythme. 

## CONSÉQUENCES
Négatives : Écrire les tables en fonction des rêquetes que l'on pourrait vouloir. Peut avoir des interminables tables, ainsi que que Eviter ALLOW FIlTERING en production