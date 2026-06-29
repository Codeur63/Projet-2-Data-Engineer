# Redis DB - Pour le cache Session de compteurs IoT SolarMboa 

## Quel est son rôle ? 

Redis est utilisé, comme clé-valeur enfin de pouvoir récuprére rapide l'accés aux session de compteur, ainsi que la concervation prioritaires au compteurs les plus actifs.

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

Pour notre projet Redis à éte configurer avec une petite mémoire afin d'éviter un consommation excessive de la machine avec la possibilié de supprimé dans son cache les clés les moins utilisée grâce : ``` conf maxmemory 256mb maxmemory-policy allkeys-lru ```

## Justification CAP

Pour rappeler un BD ne peut que avoir deux proprités, pour notre cas nous allons chercher a justifier le CAP de redis.
Avec Redis dans notre architecture nous avons le constat ou le besoin :
- La perte du cache n'est pas critique car nous pouvons toujours récuperer les informations a la source 
- Les données doivent etre toujours disponible à cause des compteurs actifs qui doivent etre recupérer rapidement
- La Tolérance qui est nécesaire en production
- La cohérance n'est pas forcement une priorité, ne pas l'avoir est acceptable

Donc le cas d'usage est AP pour notre base de données  