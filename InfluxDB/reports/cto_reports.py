"""
Rapport CTO InfluxDB — séries temporelles SolarMboa.

Objectif :
- Résumer les mesures IoT stockées dans InfluxDB
- Produire des KPI temps réel / séries temporelles
- Préparer la documentation et le dashboard
"""

from datetime import datetime

from solarmboa_influxdb.client import get_influx_client
from solarmboa_influxdb.config import settings


client = get_influx_client()
query_api = client.query_api()
bucket = settings.influxdb_bucket


START = "2025-01-01T00:00:00Z"
STOP = "2025-07-01T00:00:00Z"


def query_rows(query: str) -> list[dict]:
    tables = query_api.query(
        org=settings.influxdb_org,
        query=query,
    )

    rows = []

    for table in tables:
        for record in table.records:
            rows.append(record.values)

    return rows


def count_points() -> int:
    query = f'''
from(bucket: "{bucket}")
  |> range(start: {START}, stop: {STOP})
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "solar_output_w")
  |> count()
'''

    rows = query_rows(query)
    return int(sum(row.get("_value", 0) for row in rows))


def average_metric(metric: str) -> float:
    query = f'''
from(bucket: "{bucket}")
  |> range(start: {START}, stop: {STOP})
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "{metric}")
  |> mean()
'''

    rows = query_rows(query)

    if not rows:
        return 0.0

    values = [float(row["_value"]) for row in rows if row.get("_value") is not None]

    return sum(values) / len(values) if values else 0.0


def average_by_region(metric: str) -> list[dict]:
    query = f'''
from(bucket: "{bucket}")
  |> range(start: {START}, stop: {STOP})
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "{metric}")
  |> group(columns: ["region"])
  |> mean()
'''

    rows = query_rows(query)

    result = []

    for row in rows:
        result.append(
            {
                "region": row.get("region"),
                "value": row.get("_value"),
            }
        )

    result.sort(key=lambda x: x["value"] or 0, reverse=True)

    return result


def alerts_by_type() -> list[dict]:
    query = f'''
from(bucket: "{bucket}")
  |> range(start: {START}, stop: {STOP})
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => exists r.alert_code)
  |> group(columns: ["alert_code"])
  |> count()
'''

    rows = query_rows(query)

    result = []

    for row in rows:
        result.append(
            {
                "alert_code": row.get("alert_code"),
                "count": row.get("_value"),
            }
        )

    result.sort(key=lambda x: x["count"] or 0, reverse=True)

    return result


def print_table(rows: list[dict], key_label: str, value_label: str, value_suffix: str = ""):
    if not rows:
        print("Aucune donnée.")
        return

    for row in rows:
        key = row.get(key_label)
        value = row.get(value_label)

        if isinstance(value, float):
            value = f"{value:,.2f}"

        print(f"{str(key):<20} {value}{value_suffix}")


def main():
    print("\n" + "=" * 80)
    print("SOLARMBOA — RAPPORT CTO INFLUXDB")
    print("=" * 80)

    print(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bucket    : {bucket}")
    print(f"Période   : {START} → {STOP}")

    total_points = count_points()
    avg_solar = average_metric("solar_output_w")
    avg_battery = average_metric("battery_level_pct")
    avg_consumption = average_metric("consumption_w")

    print("\n1. KPI GLOBAUX")
    print("-" * 80)
    print(f"Points télémétrie       : {total_points:,}")
    print(f"Production moyenne      : {avg_solar:,.2f} W")
    print(f"Batterie moyenne        : {avg_battery:,.2f} %")
    print(f"Consommation moyenne    : {avg_consumption:,.2f} W")

    print("\n2. PRODUCTION MOYENNE PAR RÉGION")
    print("-" * 80)
    print_table(average_by_region("solar_output_w"), "region", "value", " W")

    print("\n3. BATTERIE MOYENNE PAR RÉGION")
    print("-" * 80)
    print_table(average_by_region("battery_level_pct"), "region", "value", " %")

    print("\n4. CONSOMMATION MOYENNE PAR RÉGION")
    print("-" * 80)
    print_table(average_by_region("consumption_w"), "region", "value", " W")

    print("\n5. ALERTES PAR TYPE")
    print("-" * 80)
    print_table(alerts_by_type(), "alert_code", "count")

    print("\nCONCLUSION CTO")
    print("-" * 80)
    print(
        "InfluxDB permet de stocker et d'analyser efficacement les mesures IoT "
        "horodatées. Elle est adaptée au suivi temps réel, aux dashboards de monitoring "
        "et aux agrégations temporelles par capteur, région et type d'alerte."
    )


if __name__ == "__main__":
    main()