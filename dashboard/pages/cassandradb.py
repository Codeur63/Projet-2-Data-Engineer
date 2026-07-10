import sys
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASSANDRA_SRC = PROJECT_ROOT / "CassandraDB" / "src"
sys.path.append(str(CASSANDRA_SRC))

from cassandradb.telemetry_repository import TelemetryRepository


st.set_page_config(
    page_title="Cassandra - SolarMboa",
    page_icon="🧱",
    layout="wide",
)

st.title("🧱 Cassandra — Ingestion massive IoT SolarMboa")

st.markdown(
    """
    Cassandra stocke l'historique long terme des mesures IoT.
    Contrairement à InfluxDB, qui sert au monitoring temps réel,
    Cassandra sert à conserver un historique massif requêtable par capteur,
    par région et par type d'alerte.
    """
)

repo = TelemetryRepository()

tab_overview, tab_sensor, tab_region, tab_alerts = st.tabs(
    ["Vue d’ensemble", "Par capteur", "Par région", "Alertes"]
)


with tab_overview:
    st.header("Rôle de Cassandra")

    c1, c2, c3 = st.columns(3)

    c1.metric("Modèle", "Query-first")
    c2.metric("Usage", "Historique IoT")
    c3.metric("Tables", "4")

    st.markdown(
        """
        ```text
        daily_stats
        └── dernières mesures d'un capteur par jour

        sensors_registry
        └── monitoring régional par jour

        sensor_alerts
        └── alertes par jour et type

        sensor_last_reading
        └── dernier état connu par région
        
        sensor_readings
        └── toutes les lectures
        ```
        """
    )

    st.info(
        "Cassandra est modélisé par requête : on duplique volontairement les données "
        "dans plusieurs tables pour éviter les scans coûteux et ALLOW FILTERING."
    )


with tab_sensor:
    st.header("Dernières mesures par capteur")

    sensor_id = st.text_input("Sensor ID", value="CAM-0001-S1")
    bucket = st.date_input("Jour", value=date.today())
    limit = st.slider("Nombre de mesures", 10, 500, 100)

    if st.button("Charger les mesures du capteur"):
        rows = repo.lire_dernieres_mesures(
            sensor_id=sensor_id,
            depuis=bucket
        )

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            if "timestamp" in df.columns and "battery_level_pct" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                st.line_chart(df.set_index("timestamp")["battery_level_pct"])
        else:
            st.warning("Aucune mesure trouvée pour ce capteur et ce jour.")


with tab_region:
    st.header("Mesures par région et par jour")

    region = st.selectbox(
        "Région",
        ["Littoral", "Centre", "Ouest", "Nord-Ouest", "Adamaoua", "Est", "Extrême-Nord"],
    )
    bucket_region = st.date_input("Jour région", value=date.today())
    limit_region = st.slider("Nombre de lignes région", 10, 1000, 200)

    if st.button("Charger les mesures régionales"):
        rows = repo.get_measures_by_region_day(
            region=region,
            bucket=bucket_region,
            limit=limit_region,
        )
               

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            if "solar_output_w" in df.columns:
                st.metric("Production moyenne", f"{df['solar_output_w'].mean():.2f} W")
            if "battery_level_pct" in df.columns:
                st.metric("Batterie moyenne", f"{df['battery_level_pct'].mean():.2f} %")
        else:
            st.warning("Aucune mesure trouvée pour cette région et ce jour.")


with tab_alerts:
    st.header("Alertes par jour")

    alert_code = st.selectbox(
        "Type d’alerte",
        [ "OVERCURRENT", "FAULT_02", "FAULT_01", "TAMPER", "OVR_V", "LOW_BAT", "NO_SIG", "ERR", "AUCUNE"],
    )
    bucket_alert = st.date_input("Jour alerte", value=date.today())
    limit_alert = st.slider("Nombre d’alertes", 10, 500, 100)

    if st.button("Charger les alertes"):
        rows = repo.get_alerts_by_day(
            bucket=bucket_alert,
            alert_code=alert_code,
            limit=limit_alert,
        )

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            if "region" in df.columns:
                by_region = df.groupby("region").size().reset_index(name="count")
                st.bar_chart(by_region.set_index("region")["count"])
        else:
            st.info("Aucune alerte trouvée pour ce jour et ce type.")