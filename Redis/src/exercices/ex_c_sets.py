"""
EXERCICE C — Sets Redis
Objectif : Maintenir des ensembles dynamiques de capteurs.
Opérations clés : SADD, SCARD, SISMEMBER, SINTER, SUNION, SDIFF.
"""

from src.cache.client import get_redis_client
from datetime import date

r = get_redis_client()
today = date.today().isoformat()

#  Ajouter des capteurs par région ──
# SADD ignore les doublons automatiquement (set = ensemble unique)
r.sadd('active:sensors:Littoral', 'CAM-0001', 'CAM-0042', 'CAM-0099', 'CAM-0101')
r.sadd('active:sensors:Centre', 'CAM-0150', 'CAM-0200', 'CAM-0250')
r.sadd('active:sensors:Ouest', 'CAM-0300', 'CAM-0318')
# TTL : les sets de capteurs actifs expirent après 10 min

r.expire('active:sensors:Littoral', 600)
r.expire('active:sensors:Centre', 600)
r.expire('active:sensors:Ouest', 600)

# Compter les capteurs actifs dans une région ──
# SCARD = Set Cardinality (taille de l'ensemble) — O(1)
count = r.scard('active:sensors:Littoral')
print(f'Capteurs actifs Littoral : {count}') 

#  Vérifier si un capteur est actif — O(1) 
is_active = r.sismember('active:sensors:Littoral', 'CAM-0042')
print(f'CAM-0042 actif ? {is_active}') # True

# Ajouter des capteurs en alerte aujourd'hui ──
r.sadd(f'alert:sensors:{today}', 'CAM-0042', 'CAM-0318', 'CAM-0200', 'CAM-0101', 'CAM-0300')
r.expire(f'alert:sensors:{today}', 600)

#  SINTER : capteurs à la fois actifs ET en alerte dans Littoral ──
# C'est la vraie puissance des Sets Redis !
alertes_littoral = r.sinter('active:sensors:Littoral', f'alert:sensors:{today}')
print(f'Alertes dans Littoral : {alertes_littoral}') # {CAM-0042}

# SUNION : tous les capteurs actifs toutes régions ──
tous_actifs = r.sunion('active:sensors:Littoral', 'active:sensors:Centre', 'active:sensors:Ouest')
print(f'Total capteurs actifs : {len(tous_actifs)}') # 9

# Retirer un capteur (suspension) ──
r.srem('active:sensors:Littoral', 'CAM-0099')
print(f'Après suspension CAM-0099 : {r.scard("active:sensors:Littoral")}') # 3