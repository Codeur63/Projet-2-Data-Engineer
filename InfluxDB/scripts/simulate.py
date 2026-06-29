import random
import time
from solarmboa_influxdb.writer import write_telemetry

SENSORS = [f"CAM-{str(i).zfill(4)}-S1" for i in range(1, 21)]
REGIONS = ['Ouest', 'Adamaoua', 'Centre', 'Littoral', 'Extrême-Nord', 'Nord-Ouest',
 'Est']


def main():
    print("+++" * 30)
    print("Simulation InfluxDB — mesures IoT")
    print("+++" * 30)
    

    # Choisir un nombre de mésuere envoyé 
    for i in range(200):
        sensor_id = random.choice(SENSORS)
        region = random.choice(REGIONS)

        solar_output_w = random.uniform(100, 3000)
        battery_level_pct = random.uniform(1, 100)
        consumption_w = random.uniform(50, 900)

        alert_code = "LOW_BAT" if battery_level_pct < 15 else None

        write_telemetry(
            sensor_id=sensor_id,
            region=region,
            solar_output_w=solar_output_w,
            battery_level_pct=battery_level_pct,
            consumption_w=consumption_w,
            alert_code=alert_code,
        )

        if i % 20 == 0:
            print(f"{i} mesures envoyées...")

        time.sleep(0.1) # Mesure envoyé toutes les millisecondes

    print("Simulation terminée.")


if __name__ == "__main__":
    main()