from cassandradb.telemetry_repository import TelemetryRepository
from datetime import datetime, date 

repo = TelemetryRepository()

# Insertion d'une ligne brute
repo.inserer_mesure(
    sensor_id="CAP-1211-S1",
    timestamp=datetime.now(),
    installation_id=2,
    solar_output_w=200,
    battery_level_pct=40,
    consumption_w=50.0,
    alert_code="FAULT_01",
    region="Adamaoua"
)


# Lecture des 100 dernières mesures

dernieres = repo.last_measure(sensor_id="CAP-1211-S1")
if dernieres:
    print(f"Premiere mesure : {dernieres} ")
else:
    print("Aucune mésure trouvé")    

# Lecture des plages horaire
# debut = datetime(2024, 1, 1, 8, 0, 0)
# fin = datetime(2024, 1, 1, 14, 0, 0)
# plage = repo.lire_plage_horaire("CAP-001", debut, fin)
# print(f"Nombre total de mesures lues : {len(plage)}")

region = repo._get_region_for_sensor('CAP-1211-S1')
print(f"La region du capteur est : {region}")