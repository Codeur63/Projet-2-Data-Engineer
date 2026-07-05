# ARCHITECTURE DECISION RECORD
## sujet : Stockage massive des données en temps réel 
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SolarMboa envoie environ 120 960 données par jour provenant des capteurs IoT, avec un besoin de stockage en temps réel à l’échelle de la seconde, de la minute ou de l’heure. Les données évoluent dans le temps et doivent être conservées 90 jours, puis supprimées automatiquement. La disponibilité est critique afin d’éviter toute perte ou corruption de données de télémétrie

## DÉCISION
SolarMboa envoie environ 120 960 données par jour provenant des capteurs IoT, avec un besoin de stockage en temps réel à l’échelle de la seconde, de la minute ou de l’heure. Les données évoluent dans le temps et doivent être conservées 90 jours, puis supprimées automatiquement. La disponibilité est critique afin d’éviter toute perte ou corruption de données de télémétrie


## POSITIONNEMENT CAP
InfluxDB est positionnée comme un système orienté AP dans notre contexte d’usage, car la disponibilité des données de télémétrie est prioritaire sur la cohérence forte immédiate. En cas de contrainte réseau ou de latence temporaire, nous privilégions la continuité de collecte et la lecture des données plutôt qu’un blocage des écritures.


## ALTERNATIVES CONSIDÉRÉES
MySQL : Supporte les données mais avec plus de 1M de données pas jour il ne pourrais pas supporter le rythme. 
PostgreSQL + partitionnement : solution possible pour des volumes modérés, mais la gestion de très fortes cadences d’écriture et de rétention par période demande davantage d’efforts d’administration et de modélisation.

## CONSÉQUENCES
Positives : stockage optimisé pour les données temporelles, requêtes rapides sur les périodes, gestion native de la rétention via bucket, bonne lisibilité des données de capteurs, et adaptation naturelle aux mesures envoyées toutes les secondes, minutes ou heures.

Négatives : il faut bien concevoir la structure des mesures, tags et fields dès le départ ; une mauvaise modélisation peut dégrader les performances. Il faut aussi éviter d’utiliser InfluxDB comme base générale pour des données métier non temporelles.

Risques mitigés : définition stricte des measurements, tags et fields, contrôle des écritures avant ingestion, supervision de la croissance des buckets, et mise en place d’une politique de rétention alignée sur les 90 jours.