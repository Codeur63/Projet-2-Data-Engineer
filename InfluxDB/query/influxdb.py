from solarmboa_influxdb.client import get_influx_client
from solarmboa_influxdb.config import settings


client = get_influx_client()
query_api = client.query_api()


def run_query(title: str, query: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    tables = query_api.query(
        org=settings.influxdb_org,
        query=query,
    )

    rows = []
    for table in tables:
        for record in table.records:
            rows.append(record.values)

    print(f"{len(rows)} ligne(s)")
    for row in rows[:10]:
        print(row)


bucket = settings.influxdb_bucket


queries = {
    "Production moyenne par région": f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "solar_output_w")
  |> group(columns: ["region"])
  |> mean()
''',

    "Batterie moyenne par région": f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "battery_level_pct")
  |> group(columns: ["region"])
  |> mean()
''',

    "Consommation moyenne par région": f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "consumption_w")
  |> group(columns: ["region"])
  |> mean()
''',

    "Nombre de points par alert_code": f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => exists r.alert_code)
  |> group(columns: ["alert_code"])
  |> count()
''',

    "Évolution temporelle CAM-0001-S1": f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r.sensor_id == "CAM-0001-S1")
  |> filter(fn: (r) => r._field == "battery_level_pct" or r._field == "solar_output_w")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_mean")
'''
}


if __name__ == "__main__":
    for title, query in queries.items():
        run_query(title, query)