"""
  SIMULTATION d'un Systeme de collecte de donnéees pour un capteur en temps réel
  Exercice A - Strings Redis
  Objectif: Comprendre SET/GET, INCR/DECR, MSET/MGET, EXPIRE, TTL, STRLEN    

"""

import time
from src.cache.client import get_redis_client
from datetime import date


# Connection sur Redis Client
r = get_redis_client()

sensor_id = 'CAM-0042-S1'
today = date.today().isoformat() 
key_sensor = f'metric:count:{sensor_id}:{today}'  

print("\n---------- Création d'un clé et métrics ----------- \n") 


# Stocker une chaine avec une expiration
r.set(key_sensor, 0, ex=300) # expire dans 5 min
print(f'Clé créée : {key_sensor}')

# Simulation de 20 mésure prise par le capteur
for _ in range(20):
  nouvelle_valeur = r.incr(key_sensor)  
  # time.sleep(1)  
  # print(f'Valeur mise à jour : {nouvelle_valeur}')

print(f"Derniere valeur du compteur : {r.get(key_sensor)}")

# Taille de stokcage de la clé avec STRLEN
taille = r.strlen(key_sensor)
print(f"La valeur '{r.get(key_sensor)}' occupe {taille} octets dans Redis.")

time.sleep(1)

# Incŕementer la valeur de la clé
r.incrby(key_sensor,5) # Incremente de 5 
print(f'Compteur après incrémentation : {r.get(key_sensor)} ')

# Voir le temps restant de la clé
ttl = r.ttl(key_sensor)
print(f'TTL restant pour la clé {key_sensor} : {ttl} secondes')


# Décrémenter la valeur de la clé
r.decrby(key_sensor, 5) # Incremente de 5 
print(f'Compteur après décrémentation : {r.get(key_sensor)} ')


# Rendre la clé permanente
r.persist(key_sensor)
print(f'Après persist, TTL de la clé {key_sensor} : {r.ttl(key_sensor)}')

# Supprimer la clé
r.delete(key_sensor)
print(f'Clé supprimée : {key_sensor} -- Valeur : {r.get(key_sensor)}')
print(f"Vérification de son existence {r.exists(key_sensor) == 1 } ")


# Enregistrement de plusieurs clé d'un coup
print("\n---------- Opération groupées ----------- \n") 
data_sensors = {
  f"sensor:status:{sensor_id}" : " ONLINE",
  f"sensor:version:{sensor_id}" : "V2.1.0",
  f"sensor:location:{sensor_id}" : "Littoral"
}

# Enregistrement de plusieur clé
r.mset(data_sensors)
print(f'Valeurs de {sensor_id}\n')
valeurs = r.mget([f"sensor:status:{sensor_id}", f"sensor:version:{sensor_id}"])
print(f"Recupération d'un coup de plusieurs valeurs via MGET : {valeurs}")

