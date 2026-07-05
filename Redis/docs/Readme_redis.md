# Redis DB - Pour le cache Session de compteurs IoT SolarMboa 

## Quel est son rôle ? 

Redis est utilisé, comme clé-valeur enfin de pouvoir récuprére rapide l'accés aux session de compteur, ainsi que la conservation prioritaires au compteurs les plus actifs.

Dans notre projet il repond au besoin de pouvoir acceder facilement ou bien rapidement aux sessions de compteur, de gerer le cache LRU des compteurs actifs

## Cas utilisé dans cette partie 
- Cache des sessions compteurs avec le Hash redis
- Pattern Cache-Aside : On accède d'abord a redis pour récupérer une valeur si on ne trouve pas la valeur on retourne vers le fichier source
- Sets Redis pour les capteurs actifs par région
- Sorted Sets pour réduire les allers et retours réseau
- Bencharmk  Redis Vs source principale
- Test LRU avec éviction automatique


## Strucutre des clés dans Redis

| Clé | Type Redis | Description | TTL |
|---|---|---|---|
| `session:sensor:{sensor_id}` | Hash | Session d’un capteur IoT | 24h ou TTL configuré |
| `active:sensors:{region}` | Set | Capteurs actifs par région | 10 min |
| `alert:sensors:{date}` | Set | Capteurs en alerte | 24h |
| `metrics:count:{sensor_id}:{date}` | String/Counter | Nombre de mesures reçues par jour | 24h |
| `leaderboard:prod:{date}` | Sorted Set | Classement production solaire | 24h |
| `get_installation_by_sensor{}` | Benchmark | Voir le temps de latence Redis Vs Source | Aucune  


## Configuration mémoire et LRU

Pour notre projet Redis à éte configurer avec une petite mémoire afin d'éviter un consommation excessive de la machine avec la possibilié de supprimé dans son cache les clés les moins utilisée grâce : ```conf maxmemory 256mb maxmemory-policy allkeys-lru```

## Justification CAP

Pour rappeler un BD ne peut que avoir deux proprités, pour notre cas nous allons chercher a justifier le CAP de redis.
Avec Redis dans notre architecture nous avons le constat ou le besoin :
- La perte du cache n'est pas critique car nous pouvons toujours récuperer les informations a la source 
- Les données doivent etre toujours disponible à cause des compteurs actifs qui doivent etre recupérer rapidement
- La Tolérance qui est nécesaire en production
- La cohérance n'est pas forcement une priorité, ne pas l'avoir est acceptable

Donc le cas d'usage est AP pour notre base de données  

## CONTEXTE
SolarMboa a besoin d’un accès rapide aux sessions des compteurs IoT, aux compteurs actifs par région et aux données les plus consultées. Le but est de réduire les accès répétés à la source principale et d’améliorer la latence des requêtes fréquentes. Le cache doit aussi supporter une logique d’éviction automatique pour conserver en priorité les données les plus actives.

## DECISION
Nous utilisons Redis comme base clé-valeur de cache pour les sessions de compteurs IoT. Les sessions seront stockées en Hash Redis, les capteurs actifs par région en Set, et les classements ou priorités métier en Sorted Set. L’accès suivra un pattern Cache-Aside : l’application interroge Redis d’abord, puis consulte la source principale si la donnée n’est pas présente, avant de réécrire le cache si nécessaire.

## POSITIONNEMENT CAP
Redis est positionné comme un système AP dans notre architecture, car la disponibilité et la rapidité d’accès sont plus importantes qu’une cohérence forte immédiate pour les données en cache. Si une clé est perdue ou évincée, la valeur peut être recalculée ou relue depuis la source principale sans bloquer le système. La tolérance aux pannes et la continuité de service priment donc sur la cohérence parfaite du cache.

## ALTERNATIVES CONSIDÉRÉES
Source principale seule : solution simple mais trop lente pour les sessions très fréquemment lues. Elle augmente la latence et la charge sur la base source.

Memcached : bon cache simple, mais moins riche que Redis en types de données et en capacités applicatives.

Base relationnelle : possible pour la persistance, mais inadaptée au rôle de cache à faible latence et à forte fréquence d’accès.

## CONSÉQUENCES
Positives : accès très rapide aux sessions, réduction des allers-retours vers la source principale, structures adaptées aux usages IoT, et gestion efficace des données actives avec TTL et éviction LRU.

Négatives : Redis ne doit pas être utilisé comme source de vérité, car les données en cache peuvent disparaître à cause de l’éviction ou du TTL. La structure des clés doit être bien définie, sinon le cache devient difficile à maintenir et à déboguer.

Risques mitigés : définir une taille mémoire limitée avec maxmemory, utiliser maxmemory-policy allkeys-lru, appliquer des TTL cohérents, monitorer le taux de cache hit/miss, et garder la source principale comme référence fonctionnelle. Les benchmarks Redis vs source principale permettront de valider le gain réel de performance.