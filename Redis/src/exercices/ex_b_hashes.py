"""
    Cache des sessions de capteurs IoT - Hash Redis
    HSET Redis, pipeline
"""


import time
from src.cache.session_cache import SessionCache, SensorSession

cache = SessionCache()
# Créer et stocker une session ──

session = SensorSession(
    sensor_id='CAM-2220-S1', 
    installation_id=20,
    region='Centre', 
    city='Yaoundé',
    tariff_plan='Standard', 
    status='inactif',
    panel_capacity=10500, 
    battery_capacity=5500,
    alert_threshold=0.40, 
    firmware_ver='v2.3.1'
)

cache.set_session(session)
print("Enregistrement du capteur... ...")
time.sleep(1) # Simuler un délai de traitement
print('Session stockée dans Redis. ✅')

#  Relire la session (doit être un HIT) ──
retrieved = cache.get_session(session.sensor_id)
print("retrieved =", retrieved)


if retrieved is None: 
    print("Session introuvable") 
else: 
    print(f'Tarif : {retrieved.tariff_plan}') # Premium
    print(f'Actif : {retrieved.is_active()}') # True


# Mettre à jour uniquement le statut ──
cache.update_status(session.sensor_id, 'actif')
updated = cache.get_session(session.sensor_id)
print(f'Nouveau statut de {cache._get_key(session.sensor_id)} : {updated.status}') # suspended

# Refressh le ttl 
cache.refresh_ttl(session.sensor_id)
print(f"TTL refresh Sensor {cache._get_key(session.sensor_id)} to 5 minutes")

print("\n--- Vérification immédiate ---")
print('Tentative de récupération.....')
time.sleep(1)
info = cache.get_session(cache._get_key(session.sensor_id))
if info:
    print(f"Succès ! Le capteur se trouve à : {info['region']}")
else:
    print(f"Erreur : Capteur introuvable dans le cache. {info}")

# Supprimer le HSET
cache.delete(session.sensor_id)
print("Cache supprimer avec succès ✅")

print("\n--- Vérification immédiate ---")
print('Tentative de récupération.....')
time.sleep(1)
info = cache.get_session(cache._get_key(session.sensor_id))
if info:
    print(f"Succès ! Le capteur se trouve à : {info['region']}")
else:
    print(f"Erreur : Capteur introuvable dans le cache. {info}")

