import sys
import time
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REDIS_DIR = PROJECT_ROOT / "Redis"
sys.path.append(str(REDIS_DIR))

from src.cache.client import get_redis_client
from src.cache.session_cache import SessionCache
from src.cache.telemetry import process_telemetry
from src.utils.data_loader import get_installation_by_sensor


st.set_page_config(
    page_title="Redis - SolarMboa",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero {
        padding: 2rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #111827 0%, #7f1d1d 55%, #f97316 120%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        font-size: 2.6rem;
        margin-bottom: 0.3rem;
    }
    .hero p {
        font-size: 1rem;
        color: #f3f4f6;
    }
    .card {
        padding: 1rem;
        border-radius: 16px;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        height: 100%;
    }
    .card h4 {
        color: #111827;
        margin-bottom: 0.35rem;
    }
    .card p {
        color: #475569;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>⚡ Redis — Cache IoT SolarMboa</h1>
        <p>
            Démonstration du rôle de Redis dans l'architecture : cache des sessions capteurs,
            TTL, LRU, pipeline, capteurs actifs, alertes batterie et leaderboard de production.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

r = get_redis_client()
cache = SessionCache()

tab_overview, tab_simulation, tab_keys, tab_leaderboard = st.tabs(
    [
        "Vue d'ensemble",
        "Simulation télémétrie",
        "Clés Redis",
        "Leaderboard",
    ]
)


# ============================================================
# 1. VUE D'ENSEMBLE
# ============================================================

with tab_overview:
    st.header("État Redis en direct")

    memory_info = r.info("memory")
    stats_info = r.info("stats")
    keyspace_info = r.info("keyspace")
    config_memory = r.config_get("maxmemory")
    config_policy = r.config_get("maxmemory-policy")

    maxmemory = int(config_memory.get("maxmemory", 0))
    maxmemory_mb = maxmemory / 1024 / 1024 if maxmemory else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Mémoire utilisée", memory_info.get("used_memory_human"))
    col2.metric("Limite mémoire", f"{maxmemory_mb:.0f} MB")
    col3.metric("Politique mémoire", config_policy.get("maxmemory-policy"))
    col4.metric("Evicted keys", stats_info.get("evicted_keys"))

    st.markdown("### Processus Redis dans l'architecture")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="card">
                <h4>1. Capteur IoT</h4>
                <p>Un compteur envoie production solaire, batterie, consommation et région.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="card">
                <h4>2. Pipeline Redis</h4>
                <p>Plusieurs écritures sont envoyées en un seul lot pour réduire la latence.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="card">
                <h4>3. Cache & TTL</h4>
                <p>Les sessions et métriques temporaires expirent automatiquement.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            """
            <div class="card">
                <h4>4. LRU</h4>
                <p>Quand la mémoire est pleine, Redis évince les clés les moins récemment utilisées.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Keyspace Redis")
    st.json(keyspace_info)

    st.markdown(
        """
        ```text
        Capteurs IoT
             ↓
        API / ingestion
             ↓
        Redis
          ├── sensor:session:{sensor_id}
          ├── metrics:count:{sensor_id}:{date}
          ├── active:sensors:{region}
          ├── alert:sensors:{date}
          └── leaderboard:prod:{date}
             ↓
        MongoDB / Cassandra / InfluxDB / Data Lake
        ```
        """
    )


# ============================================================
# 2. SIMULATION TÉLÉMÉTRIE
# ============================================================

with tab_simulation:
    st.header("Simulation d'une mesure IoT")

    st.write(
        "Cette section déclenche réellement `process_telemetry()` et met à jour Redis."
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Mesure manuelle")

        sensor_id = st.text_input("Sensor ID", value="CAM-0001-S1")

        region = st.selectbox(
            "Région",
            [
                "Littoral",
                "Centre",
                "Ouest",
                "Nord-Ouest",
                "Adamaoua",
                "Est",
                "Extrême-Nord",
            ],
        )

        solar_output_w = st.slider(
            "Production solaire (W)",
            min_value=0.0,
            max_value=2000.0,
            value=650.0,
            step=10.0,
        )

        battery_pct = st.slider(
            "Batterie (%)",
            min_value=0.0,
            max_value=100.0,
            value=72.0,
            step=1.0,
        )

        consumption_w = st.slider(
            "Consommation (W)",
            min_value=0.0,
            max_value=1500.0,
            value=250.0,
            step=10.0,
        )

        simulate_one = st.button(
            "Déclencher process_telemetry()",
            type="primary",
        )

        st.divider()

        st.subheader("Simulation de masse")

        nb_sensors = st.slider(
            "Nombre de capteurs à simuler",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
        )

        simulate_many = st.button("Simuler plusieurs capteurs")

    with col_right:
        st.subheader("Résultat")

        if simulate_one:
            start = time.perf_counter()

            result = process_telemetry(
                sensor_id=sensor_id,
                solar_output_w=solar_output_w,
                battery_pct=battery_pct,
                consumption_w=consumption_w,
                region=region,
            )

            elapsed_ms = (time.perf_counter() - start) * 1000

            st.success(f"Mesure traitée en {elapsed_ms:.3f} ms")
            st.json(result)

        if simulate_many:
            regions = [
                "Littoral",
                "Centre",
                "Ouest",
                "Nord-Ouest",
                "Adamaoua",
                "Est",
                "Extrême-Nord",
            ]

            start = time.perf_counter()

            for i in range(1, nb_sensors + 1):
                process_telemetry(
                    sensor_id=f"CAM-{str(i).zfill(4)}-S1",
                    solar_output_w=300 + i * 25,
                    battery_pct=max(5, 90 - i),
                    consumption_w=120 + i * 8,
                    region=regions[i % len(regions)],
                )

            elapsed_ms = (time.perf_counter() - start) * 1000

            st.success(
                f"{nb_sensors} capteurs simulés en {elapsed_ms:.3f} ms"
            )

            st.info(
                "Les capteurs ont été ajoutés aux Sets actifs, aux compteurs journaliers "
                "et au leaderboard de production."
            )

        st.markdown("### Clés mises à jour")

        today = date.today().isoformat()

        keys_to_check = {
            "Compteurs journaliers": f"metrics:count:*:{today}",
            "Capteurs actifs": "active:sensors:*",
            "Alertes batterie": f"alert:sensors:{today}",
            "Leaderboard production": f"leaderboard:prod:{today}",
        }

        for label, pattern in keys_to_check.items():
            matched = list(r.scan_iter(pattern))
            st.write(f"**{label}** : {len(matched)} clé(s)")
            if matched:
                st.code("\n".join(matched[:10]))

    st.divider()

    st.subheader("Cache-Aside : HIT / MISS")

    h1, h2, h3 = st.columns(3)

    if h1.button("Lire session depuis Redis"):
        start = time.perf_counter()
        session = cache.get_session(sensor_id)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if session:
            st.success(f"HIT Redis — {elapsed_ms:.3f} ms")
            st.json(session.__dict__)
        else:
            st.warning(f"MISS Redis — {elapsed_ms:.3f} ms")

    if h2.button("Lire depuis la source"):
        start = time.perf_counter()
        installation = get_installation_by_sensor(sensor_id)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if installation:
            st.info(f"Lecture source — {elapsed_ms:.3f} ms")
            st.json(installation)
        else:
            st.error("Installation introuvable dans la source.")

    if h3.button("Supprimer session du cache"):
        cache.delete(sensor_id)
        st.warning(f"Session supprimée : sensor:session:{sensor_id}")


# ============================================================
# 3. CLÉS REDIS
# ============================================================

with tab_keys:
    st.header("Exploration des clés Redis")

    pattern = st.text_input("Pattern Redis", value="*")

    if st.button("Scanner Redis"):
        keys = list(r.scan_iter(pattern))

        st.write(f"{len(keys)} clé(s) trouvée(s)")

        rows = []

        for key in keys[:500]:
            rows.append(
                {
                    "key": key,
                    "type": r.type(key),
                    "ttl": r.ttl(key),
                }
            )

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("Aucune clé trouvée.")


# ============================================================
# 4. LEADERBOARD
# ============================================================

with tab_leaderboard:
    st.header("Leaderboard de production solaire")

    leaderboard_keys = list(r.scan_iter("leaderboard:prod:*"))

    if not leaderboard_keys:
        st.info(
            "Aucun leaderboard trouvé. Lance d'abord une simulation dans l'onglet Simulation télémétrie."
        )
    else:
        selected_lb = st.selectbox(
            "Leaderboard disponible",
            leaderboard_keys,
        )

        show_all = st.checkbox(
            "Afficher tous les capteurs du leaderboard",
            value=True,
        )

        if show_all:
            data = r.zrevrange(selected_lb, 0, -1, withscores=True)
        else:
            top_n = st.slider(
                "Top N",
                min_value=5,
                max_value=50,
                value=10,
            )
            data = r.zrevrange(selected_lb, 0, top_n - 1, withscores=True)

        if data:
            df = pd.DataFrame(data, columns=["sensor_id", "production_wh"])
            df["production_wh"] = df["production_wh"].astype(float)
            df["production_kwh"] = df["production_wh"] / 1000

            col_a, col_b, col_c = st.columns(3)

            col_a.metric("Nombre de capteurs", len(df))
            col_b.metric(
                "Production totale",
                f"{df['production_kwh'].sum():.3f} kWh",
            )
            col_c.metric(
                "Meilleur capteur",
                str(df.iloc[0]["sensor_id"]),
            )

            st.dataframe(df, use_container_width=True)

            st.bar_chart(
                df.set_index("sensor_id")["production_wh"],
                use_container_width=True,
            )
        else:
            st.info("Leaderboard vide.")