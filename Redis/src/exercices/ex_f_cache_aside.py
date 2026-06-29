"""
EXERCICE F — Pattern Cache-Aside complet.
Implémentation de get_session_with_fallback() avec mesure des performances.
"""
import time, logging
from typing import Optional
from src.cache.session_cache import SessionCache, SensorSession
from src.utils.data_loader import get_installation_by_sensor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
cache = SessionCache()

def get_session_with_fallback(sensor_id: str) -> Optional[SensorSession]:
    """
    Pattern Cache-Aside :
    1. Chercher dans Redis (HIT → retourner immédiatement)
    2. En cas de MISS → charger depuis la source (JSON/MySQL)
    3. Stocker dans Redis avec TTL pour le prochain appel
    4. Retourner les données
    """
    t0 = time.perf_counter()
    # ── ÉTAPE 1 : Lecture Redis ──
    session = cache.get_session(sensor_id)
    if session is not None:
        elapsed = (time.perf_counter() - t0) * 1000
        logger.info(f'HIT [{sensor_id}] — {elapsed:.2f}ms')
        return session
    # ── ÉTAPE 2 : MISS → Fallback source de données ──
    logger.info(f'MISS [{sensor_id}] — chargement depuis source...')
    inst = get_installation_by_sensor(sensor_id)
    
    if inst is None:
        logger.warning(f'Installation introuvable pour {sensor_id}')
        return None
    
# ── ÉTAPE 3 : Construire et cacher la session ──
    session = SensorSession(
        sensor_id=sensor_id,
        installation_id=inst.get('installation_id', 0),
        region=inst.get('region', 'unknown'),
        city=inst.get('city', 'unknown'),
        tariff_plan=inst.get('tariff_plan', 'Basic'),
        status=inst.get('status', 'active'),
        panel_capacity=inst.get('panel_capacity_wp', 250),
        battery_capacity=inst.get('battery_capacity_wh', 1000),
        alert_threshold=0.40,
        firmware_ver='v2.0.0',
    )
    cache.set_session(session)
    elapsed = (time.perf_counter() - t0) * 1000
    logger.info(f'    CACHED [{sensor_id}] — {elapsed:.2f}ms (fallback)')
    
    return session


# ── Benchmark Cache-Aside ──
if __name__ == '__main__':
    test_sensors = ['CAM-0042-S1', 'CAM-0001-S1', 'CAM-0100-S1',
    'CAM-0042-S1', 'CAM-0001-S1', 'CAM-0042-S1', 'CAM-0597-S2']
    print('\n=== BENCHMARK CACHE-ASIDE ===')
    times_miss, times_hit = [], []
    
    # Premier passage : tous MISSes
    print('\n--- Premier passage (MISSes attendus) ---')
    for sid in test_sensors[:3]:
        t0 = time.perf_counter()
        get_session_with_fallback(sid)
        times_miss.append((time.perf_counter() - t0) * 1000)
        
    # Deuxième passage : tous HITs (sessions dans Redis)
    print('\n--- Deuxième passage (HITs attendus) ---')
    for sid in test_sensors:
        t0 = time.perf_counter()
        get_session_with_fallback(sid)
        times_hit.append((time.perf_counter() - t0) * 1000)
        
    if times_miss and times_hit:
        gain = sum(times_miss)/len(times_miss) / (sum(times_hit)/len(times_hit))
        print(f'\nMISS moyen : {sum(times_miss)/len(times_miss):.2f}ms')
        print(f'HIT moyen : {sum(times_hit)/len(times_hit):.2f}ms')
        print(f'Gain cache : ×{gain:.0f} plus rapide avec le cache')