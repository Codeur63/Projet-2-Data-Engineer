import time
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from solarmboa_influxdb.client import get_influx_client
from solarmboa_influxdb.config import settings


load_dotenv()


CSV_PATH = os.getenv("SENSOR_TELEMETRY")

def main():
    print("Chargement CSV :", CSV_PATH)

    df = pd.read_csv(CSV_PATH)
    print(f"Lignes chargées : {len(df):,}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    df = df.dropna(subset=["sensor_id", "installation_id", "timestamp"])
    print(f"Lignes valides après nettoyage : {len(df):,}")

    client = get_influx_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch_size = 5000 # Inserer par pas de 5000
    total_written = 0 

    start = time.perf_counter()  # Mesure du temps

    for start_idx in range(0, len(df), batch_size):
        batch = df.iloc[start_idx:start_idx + batch_size]

        points = []

        for _, row in batch.iterrows():
            point = (
                Point("sensor_telemetry")
                .tag("sensor_id", str(row["sensor_id"]))
                .tag("installation_id", str(row["installation_id"]))
                .tag("region", str(row["region"]))
                .field("solar_output_w", float(row["solar_output_w"]))
                .field("battery_level_pct", float(row["battery_level_pct"]))
                .field("consumption_w", float(row["consumption_w"]))
                .time(row["timestamp"].to_pydatetime(), WritePrecision.NS)
            )

            if pd.notna(row.get("alert_code")):
                point = point.tag("alert_code", str(row["alert_code"]))

            points.append(point)

        write_api.write(
            bucket=settings.influxdb_bucket,
            org=settings.influxdb_org,
            record=points,
        )

        total_written += len(points)
        print(f"{total_written:,} points écrits...")

    elapsed = time.perf_counter() - start # Calcule du temps depuis l'exécution 

    print("\nImport terminé.")
    print(f"Total écrit : {total_written:,} points")
    print(f"Durée       : {elapsed:.2f} sec")
    print(f"Débit       : {total_written / elapsed:,.0f} points/sec")


if __name__ == "__main__":
    main()