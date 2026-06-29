import time
from src.cache.telemetry import process_telemetry

print("--- Réception d'une mesure IoT ---")
time.sleep(1)

# ── Simulation de 100 mesures IoT ──
sensors = [f'CAM-{str(i).zfill(4)}-S1' for i in range(1, 11)]
regions = ['Littoral', 'Centre', 'Ouest', 'Nord-Ouest', 'Adamaoua']
start = time.perf_counter()

for i in range(100):
    result = process_telemetry(
        sensor_id=sensors[i % 10],
        solar_output_w=400 + (i * 2),
        battery_pct=80 - (i * 0.5),
        consumption_w=120.0,
        region=regions[i % 5],
    )
# production variable
# batterie qui baisse

elapsed = time.perf_counter() - start
print(f'100 mesures traitées en {elapsed*1000:.1f}ms')
print(f'Moyenne : {elapsed*10:.2f}ms par mesure')

# Vérifier les résultats dans redis-cli :
# redis-cli KEYS 'leaderboard:prod:*'
# redis-cli ZREVRANGE leaderboard:prod:2025-06-15 0 9 WITHSCORES
# redis-cli SMEMBERS active:sensors:Littoral