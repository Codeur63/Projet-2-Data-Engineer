import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFLUX_SRC = PROJECT_ROOT / "InfluxDB" / "src"
sys.path.append(str(INFLUX_SRC))

from solarmboa_influxdb.client import get_influx_client
from solarmboa_influxdb.config import settings


st.set_page_config(
    page_title="InfluxDB - SolarMboa",
    page_icon="📈",
    layout="wide",
)

st.title("📈 InfluxDB — Télémétrie IoT SolarMboa")

st.markdown(
    """
    InfluxDB stocke les mesures temporelles des capteurs :
    production solaire, batterie, consommation et alertes.
    """
)

client = get_influx_client()
query_api = client.query_api()
bucket = settings.influxdb_bucket


def query_to_dataframe(flux_query: str) -> pd.DataFrame:
    tables = query_api.query(org=settings.influxdb_org, query=flux_query)

    rows = []
    for table in tables:
        for record in table.records:
            rows.append(record.values)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


tab_overview, tab_regions, tab_alerts, tab_sensor = st.tabs(
    ["Vue d’ensemble", "Régions", "Alertes", "Capteur"]
)


with tab_overview:
    st.header("Vue d’ensemble InfluxDB")

    count_query = f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "solar_output_w")
  |> count()
'''

    df_count = query_to_dataframe(count_query)

    total_points = int(df_count["_value"].sum()) if not df_count.empty else 0

    avg_battery_query = f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "battery_level_pct")
  |> mean()
'''

    df_battery = query_to_dataframe(avg_battery_query)
    avg_battery = df_battery["_value"].mean() if not df_battery.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Points télémétrie", f"{total_points:,}")
    c2.metric("Batterie moyenne", f"{avg_battery:.1f} %")
    c3.metric("Bucket", bucket)

    st.info(
        "InfluxDB est utilisé pour les données temporelles récentes : "
        "visualisation, monitoring et tendances capteurs."
    )


with tab_regions:
    st.header("Analyse par région")

    metric = st.selectbox(
        "Métrique",
        ["solar_output_w", "battery_level_pct", "consumption_w"],
    )

    region_query = f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r._field == "{metric}")
  |> group(columns: ["region"])
  |> mean()
'''

    df_region = query_to_dataframe(region_query)

    if df_region.empty:
        st.warning("Aucune donnée trouvée.")
    else:
        df = df_region[["region", "_value"]].rename(columns={"_value": metric})
        df = df.sort_values(metric, ascending=False)

        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("region")[metric])


with tab_alerts:
    st.header("Alertes capteurs")

    alert_query = f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => exists r.alert_code)
  |> group(columns: ["alert_code"])
  |> count()
'''

    df_alerts = query_to_dataframe(alert_query)

    if df_alerts.empty:
        st.info("Aucune alerte trouvée.")
    else:
        df = df_alerts[["alert_code", "_value"]]
        df = df.groupby("alert_code", as_index=False)["_value"].sum()
        df = df.rename(columns={"_value": "count"})
        df = df.sort_values("count", ascending=False)

        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("alert_code")["count"])


with tab_sensor:
    st.header("Évolution temporelle par capteur")

    sensor_id = st.text_input("Sensor ID", value="CAM-0001-S1")

    sensor_metric = st.selectbox(
        "Métrique capteur",
        ["solar_output_w", "battery_level_pct", "consumption_w"],
        key="sensor_metric",
    )

    sensor_query = f'''
from(bucket: "{bucket}")
  |> range(start: 2025-01-01T00:00:00Z, stop: 2025-07-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "sensor_telemetry")
  |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
  |> filter(fn: (r) => r._field == "{sensor_metric}")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
'''

    df_sensor = query_to_dataframe(sensor_query)

    if df_sensor.empty:
        st.warning("Aucune donnée pour ce capteur.")
    else:
        df = df_sensor[["_time", "_value"]].rename(
            columns={"_time": "date", "_value": sensor_metric}
        )
        df["date"] = pd.to_datetime(df["date"])

        st.dataframe(df, use_container_width=True)
        st.line_chart(df.set_index("date")[sensor_metric])