# ARCHITECTURE DECISION RECORD
## sujet : Stockage des rélations entre les CSV
### Statut : APPROUVÉ | Date: Mars 2026 | Auteur: Équipe Data

## CONTEXTE
SolarMboa gère environ 4 800 installations solaires, avec des distributeurs qui vendent les installations, des techniciens qui assurent la maintenance, et des régions associées à chaque entité. Nous devons exécuter rapidement des requêtes de corrélation entre plusieurs ensembles de données afin d’identifier les liens entre installations, distributeurs, techniciens et zones géographiques. La cohérence est nécessaire pour éviter les erreurs d’affectation ou d’installation.  

## DÉCISION
SolarMboa gère environ 4 800 installations solaires, avec des distributeurs qui vendent les installations, des techniciens qui assurent la maintenance, et des régions associées à chaque entité. Nous devons exécuter rapidement des requêtes de corrélation entre plusieurs ensembles de données afin d’identifier les liens entre installations, distributeurs, techniciens et zones géographiques. La cohérence est nécessaire pour éviter les erreurs d’affectation ou d’installation.  


## POSITIONNEMENT CAP
Neo4j est positionné comme un système CP dans notre contexte, car la cohérence des relations est prioritaire pour garantir des résultats fiables lors des requêtes métier. En cas de conflit ou d’incohérence, il vaut mieux préserver l’intégrité du graphe que retourner un résultat erroné. Les relations étant au cœur du modèle, toute erreur de liaison pourrait provoquer une mauvaise attribution de technicien ou de distributeur.
   

## ALTERNATIVES CONSIDÉRÉES 
MySQL avec CSV : possible pour stocker les données tabulaires, mais les jointures deviennent rapidement lourdes et lentes lorsque les relations sont nombreuses. Ce modèle convient moins bien aux parcours relationnels complexes que Neo4j.

PostgreSQL : puissant et cohérent, mais moins naturel qu’un graphe pour représenter des relations multiples entre installations, techniciens, distributeurs et régions.

## CONSÉQUENCES
Positives : modèle intuitif pour les relations, requêtes plus simples et plus rapides sur les connexions entre entités, meilleure lisibilité des dépendances métier, et adaptation naturelle aux cas d’usage orientés graphe.

Négatives : il faut bien modéliser le graphe dès le départ, car le schéma doit être pensé autour des relations et des requêtes cibles. Neo4j Community a aussi des limites fonctionnelles par rapport à l’édition Enterprise, notamment pour les déploiements plus avancés.

Risques mitigés : définir des labels et relations clairs, éviter les propriétés inutiles sur les liens, tester les requêtes Cypher les plus fréquentes, et documenter les chemins de navigation attendus. Il faut aussi prévoir une stratégie d’évolution du graphe si le volume ou la complexité des relations augmente.