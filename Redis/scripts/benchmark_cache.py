"""
    Comparaison de la latence entre  la lecture de la donnée depuis redis et la 
    lecture de la donnée depuis la source
    
    Ensuire de pouvoir faire les Tests LRU avec pour objectif 
        - Remplir avec beaucoup de clés 
        - atteindre la limite de mémoire
        - Prouver que lRU Augmente

"""


import time
import statistics
from typing import Optional, Callable
from src.cache.client import get_redis_client
from src.cache.session_cache import SessionCache, SensorSession
from src.utils.data_loader import get_installation_by_sensor

cache = SessionCache()


TEST_SENSORS = [
    "CAM-0001-S1",
    "CAM-0042-S1",
    "CAM-0100-S1",
    "CAM-0200-S1",
    "CAM-0300-S1",
]

def measure(fn:Callable, iter: int=50) -> list[float]:
    times=[]
    
    for _ in range(iter):
        start = time.perf_counter()
        fn()
        elapsed_md = (time.perf_counter() - start ) * 1000
        times.append(elapsed_md)
        
    return times


def load_from_sources(sensor_id:str) -> Optional[dict]:
    return get_installation_by_sensor(sensor_id)


def load_from_redis(sensor_id:str):
    return cache.get_session(sensor_id)


def warm_cache(sensor_id:str):
    installation = get_installation_by_sensor(sensor_id)
    
    if  installation is None:
        return None 
    
    session = SensorSession(
        sensor_id=sensor_id,
        installation_id=installation.get("installation_id", 0),
        region=installation.get("region", "unknown"),
        city=installation.get("city", "unknown"),
        tariff_plan=installation.get("tariff_plan", "Basic"),
        status=installation.get("status", "active"),
        panel_capacity=installation.get("panel_capacity_wp", 0),
        battery_capacity=installation.get("battery_capacity_wh", 0),
        alert_threshold=0.40,
        firmware_ver="v2.0.0",
    )   
    
    cache.set_session(session)
    
    
def summarize(label: str, times: list[float]) -> dict:
       
    return {
        "label": label,
        "avg_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times),
    }
    
    
def print_summary(summary: dict):
    print(
        f"{summary['label']:<25} "
        f"avg={summary['avg_ms']:.3f} ms | "
        f"median={summary['median_ms']:.3f} ms | "
        f"min={summary['min_ms']:.3f} ms | "
        f"max={summary['max_ms']:.3f} ms"
    )
    
    
 # Configuration d'une memoire tres faible 
 
def print_config(r):
    maxmemory = r.config_get("maxmemory").get("maxmemory")
    policy = r.config_get("maxmemory-policy").get("maxmemory-policy")

    print("\n=== CONFIG REDIS ===")
    print(f"maxmemory        : {int(maxmemory) / 1024 / 1024:.2f} MB")
    print(f"maxmemory-policy : {policy}")


def print_stats(r, label):
    info = r.info("stats")
    memory = r.info("memory")

    print(f"\n=== {label} ===")
    print(f"used_memory_human : {memory.get('used_memory_human')}")
    print(f"evicted_keys      : {info.get('evicted_keys')}")
    print(f"keyspace_hits     : {info.get('keyspace_hits')}")
    print(f"keyspace_misses   : {info.get('keyspace_misses')}")
   
    
def config_mem():
    r = get_redis_client()

    print("\n=== TEST OFFICIEL LRU REDIS ===")

    print_config(r)

    # Nettoyage uniquement des clés de test
    for key in r.scan_iter("lru:test:*"):
        r.delete(key)

    print_stats(r, "AVANT INSERTION")

    # On crée une valeur assez lourde pour forcer Redis à évincer
    payload = "x" * 10_000  # environ 10 KB par clé

    print("\nInsertion de clés de test...")
    inserted = 0

    for i in range(100_000):
        key = f"lru:test:{i}"
        r.set(key, payload)

        # On relit certaines clés pour les rendre "récemment utilisées"
        if i % 100 == 0:
            r.get(key)

        inserted += 1

        if i % 1000 == 0 and i > 0:
            evicted = r.info("stats").get("evicted_keys")
            used_mem = r.info("memory").get("used_memory_human")
            print(f"{i} clés insérées | mémoire={used_mem} | evicted_keys={evicted}")
            time.sleep(0.5)

        if r.info("stats").get("evicted_keys", 0) > 0:
            break

    print_stats(r, "APRÈS INSERTION")

    existing_keys = sum(1 for _ in r.scan_iter("lru:test:*"))

    print("\n=== RÉSULTAT ===")
    print(f"Clés insérées       : {inserted}")
    print(f"Clés encore présentes : {existing_keys}")
    print(f"Clés évincées Redis : {r.info('stats').get('evicted_keys')}")

    if r.info("stats").get("evicted_keys", 0) > 0:
        print("\n✅ LRU validé : Redis a évincé des clés quand la mémoire maximale a été atteinte.")
    else:
        print("\n⚠️ Aucune éviction observée. Diminue maxmemory dans redis.conf, ex: maxmemory 16mb.")

    time.sleep(1)    

    
    
if __name__ == '__main__':
    print("\n === Benchmark De Redis Cache-Aside ===\n")
    
    sensor_id = TEST_SENSORS[0]
    
    
    print(f'Capteur testé : {sensor_id} ')
    
    # Nettoyage
    cache.delete(sensor_id)
    
    # Mesure de la lecture
    source_times = measure(lambda: load_from_sources(sensor_id), iter=50)
    
    # Warm cache
    warm_cache(sensor_id)
    
    # Mesure lecture Redis
    redis_times = measure(lambda: load_from_redis(sensor_id), iter=50)
    
    source_summary = summarize('Lecture source ', source_times)
    redis_summary  = summarize('Lecture Redis ', redis_times)
    
    print_summary(source_summary)
    print_summary(redis_summary)
    
    gain = source_summary['avg_ms'] / redis_summary['avg_ms']

    print(f"\nGain moyen redis : x{gain:.1f}")
    
    print(f"\n Conclusion ------ -------- -------- --------\n")
    
    print("Redis reduit  la latence moyenne de lecture des sessions  capteurs en evitant de relire systématiquement la source principale.")    
    
    print("\n --------- \n")
    
    config_mem()
    
        