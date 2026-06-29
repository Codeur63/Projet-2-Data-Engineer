"""
Traitement d'une mesure IoT avec Pipeline Redis.
7 opérations Redis en 1 seul round-trip réseau.
"""
import os
from datetime import date
from src.cache.client import get_redis_client

SESSION_TTL = int(os.getenv('SESSION_TTL', 300))
ACTIVE_SET_TTL = 600 # 10 min
COUNTER_TTL = 86400 # 24h
ALERT_SET_TTL = 86400 # 24h
LEADERBOARD_TTL = 86400 # 24h
BATTERY_LOW_PCT = 15.0

# Seuil alerte batterie
def process_telemetry(
        sensor_id: str,
        solar_output_w: float,
        battery_pct:  float,
        consumption_w: float,
        region: str ) -> dict:
    """
    Traite une mesure IoT — toutes les écritures Redis en 1 Pipeline.
    
    Args:
        sensor_id : Identifiant du capteur (ex: 'CAM-0042-S1')
        solar_output_w : Production solaire en Watts
        battery_pct : Niveau de batterie en %
        consumption_w : Consommation en Watts
        region : Région géographique 
   
    Returns:
        dict avec les résultats de chaque opération Pipeline.
    """
    r = get_redis_client()
    today = date.today().isoformat()
    wh = (solar_output_w * 30) / 3600 if solar_output_w else 0
    
    # transaction=False : plus rapide, mais pas atomique
    # Utiliser transaction=True uniquement si atomicité requise
    
    pipe = r.pipeline(transaction=False)
    
    # ── Commande 1 : Refresh TTL de la session (keepalive) ──
    pipe.expire(f'session:sensor:{sensor_id}', SESSION_TTL)
    
    # ── Commande 2 : Incrémenter compteur de mesures du jour ──
    counter_key = f'metrics:count:{sensor_id}:{today}'
    pipe.incr(counter_key)
    pipe.expire(counter_key, COUNTER_TTL)
    
    # ── Commande 4 : Mise à jour du leaderboard (si production solaire) ──
    
    if wh > 0:
        lb_key = f'leaderboard:prod:{today}'
        pipe.zincrby(lb_key, wh, sensor_id)
        pipe.expire(lb_key, LEADERBOARD_TTL)
        
# ── Commande 6 : Marquer comme capteur actif dans sa région ──

    active_key = f'active:sensors:{region}'
    pipe.sadd(active_key, sensor_id)
    pipe.expire(active_key, ACTIVE_SET_TTL)
    
# ── Commande 8 : Alerte si batterie faible ──
    if battery_pct < BATTERY_LOW_PCT:
        alert_key = f'alert:sensors:{today}'
        pipe.sadd(alert_key, sensor_id)
        pipe.expire(alert_key, ALERT_SET_TTL)
        
    # ─── Exécution : toutes les commandes en 1 round-trip ───
    results = pipe.execute()
    
    return{
        'sensor_id':  sensor_id,
        'wh_added':   wh,
        'battery_pct': battery_pct,
        'low_battery': battery_pct < BATTERY_LOW_PCT,
        'pipeline_ops': len(results),
    }