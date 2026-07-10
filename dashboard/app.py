from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="SolarMboa BI Dashboard", page_icon="☀️", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {padding: 2rem; border-radius: 22px; background: linear-gradient(120deg,#0f172a 0%,#14532d 55%,#facc15 140%); color: white; margin-bottom: 1.4rem;}
.hero h1 {font-size: 2.4rem; margin-bottom: .3rem;}
.hero p {font-size: 1rem; color: #e5e7eb; margin-bottom: 0;}
.section-title {font-size: 1.35rem; font-weight: 700; margin-top: 1.4rem; margin-bottom: .6rem; color:#0f172a;}
.insight-box {padding: 1rem 1.2rem; border-radius: 16px; background:#f8fafc; border-left: 5px solid #22c55e; margin-bottom: 1rem;}
.small-muted {color:#64748b; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    path = WAREHOUSE_DIR / f"{table_name}.csv"
    if not path.exists():
        st.warning(f"Table manquante : {path}")
        return pd.DataFrame()
    return pd.read_csv(path)

# Tables du Data Warehouse
dim_region = load_table("dim_region")
dim_date = load_table("dim_date")
dim_installation = load_table("dim_installation")
dim_distributor = load_table("dim_distributor")
dim_technician = load_table("dim_technician")
dim_contract_plan = load_table("dim_contract_plan")
fact_telemetry_daily = load_table("fact_telemetry_daily")
fact_payments = load_table("fact_payments")
fact_sales_network = load_table("fact_sales_network")

def prepare_payments() -> pd.DataFrame:
    if fact_payments.empty or dim_installation.empty:
        return pd.DataFrame()
    cols = ["installation_key", "installation_id", "region_key", "client_type", "status", "contract_plan"]
    cols = [c for c in cols if c in dim_installation.columns]
    df = fact_payments.merge(dim_installation[cols], on="installation_key", how="left")
    if not dim_region.empty and "region_key" in df.columns:
        df = df.merge(dim_region[["region_key", "region_name"]], on="region_key", how="left")
    if not dim_date.empty and "date_key" in df.columns:
        df = df.merge(dim_date[["date_key", "full_date", "month", "year"]], on="date_key", how="left")
        df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")
    return df

def prepare_telemetry() -> pd.DataFrame:
    if fact_telemetry_daily.empty or dim_installation.empty:
        return pd.DataFrame()
    cols = ["installation_key", "installation_id", "region_key", "client_type", "status", "contract_plan"]
    cols = [c for c in cols if c in dim_installation.columns]
    df = fact_telemetry_daily.merge(dim_installation[cols], on="installation_key", how="left")
    if not dim_region.empty and "region_key" in df.columns:
        df = df.merge(dim_region[["region_key", "region_name"]], on="region_key", how="left")
    if not dim_date.empty and "date_key" in df.columns:
        df = df.merge(dim_date[["date_key", "full_date", "month", "year"]], on="date_key", how="left")
        df["full_date"] = pd.to_datetime(df["full_date"], errors="coerce")
    return df

def prepare_sales_network() -> pd.DataFrame:
    if fact_sales_network.empty:
        return pd.DataFrame()
    df = fact_sales_network.copy()
    if not dim_distributor.empty and "distributor_key" in df.columns:
        df = df.merge(dim_distributor[["distributor_key", "distributor_name"]], on="distributor_key", how="left")
    if not dim_technician.empty and "technician_key" in df.columns:
        df = df.merge(dim_technician[["technician_key", "technician_name"]], on="technician_key", how="left")
    return df

payments = prepare_payments()
telemetry = prepare_telemetry()
sales_network = prepare_sales_network()

# Sidebar
st.sidebar.title("Filtres")
regions = sorted(telemetry["region_name"].dropna().unique()) if not telemetry.empty and "region_name" in telemetry.columns else []
client_types = sorted(dim_installation["client_type"].dropna().unique()) if not dim_installation.empty and "client_type" in dim_installation.columns else []
contracts = sorted(dim_installation["contract_plan"].dropna().unique()) if not dim_installation.empty and "contract_plan" in dim_installation.columns else []
selected_regions = st.sidebar.multiselect("Régions", regions, default=regions)
selected_client_types = st.sidebar.multiselect("Types de clients", client_types, default=client_types)
selected_contracts = st.sidebar.multiselect("Plans tarifaires", contracts, default=contracts)

if not telemetry.empty:
    telemetry_filtered = telemetry[
    telemetry["region_name"].isin(selected_regions)
    & telemetry["client_type"].isin(selected_client_types)
    & telemetry["contract_plan"].isin(selected_contracts)
    ]
else:
    telemetry_filtered = telemetry


if not payments.empty:
    payments_filtered = payments[
    payments["region_name"].isin(selected_regions)
    & payments["client_type"].isin(selected_client_types)
    & payments['contract_plan'].isin(selected_contracts)
    ]
else:
    payments_filtered = payments

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "region_name" in out.columns and selected_regions:
        out = out[out["region_name"].isin(selected_regions)]
    if "client_type" in out.columns and selected_client_types:
        out = out[out["client_type"].isin(selected_client_types)]
    if "contract_plan" in out.columns and selected_contracts:
        out = out[out["contract_plan"].isin(selected_contracts)]
    return out

telemetry_f = apply_filters(telemetry)
payments_f = apply_filters(payments)

# Header
st.markdown("""
<div class="hero">
  <h1>☀️ SolarMboa Dashboard</h1>
  <p>Pilotage de la production solaire, des revenus, des alertes et de l'état du parc à partir du Data Warehouse.</p>
</div>
""", unsafe_allow_html=True)



# KPI
total_installations = dim_installation["installation_id"].nunique() if not dim_installation.empty and "installation_id" in dim_installation.columns else 0

active_installations = dim_installation.query("status == 'active'")["installation_id"].nunique() if not dim_installation.empty and "status" in dim_installation.columns else 0

maintenance_installations = dim_installation.query("status == 'maintenance'")["installation_id"].nunique() if not dim_installation.empty and "status" in dim_installation.columns else 0

total_revenue = payments_f["amount_xaf"].sum() if not payments_f.empty and "amount_xaf" in payments_f.columns else 0

expected_revenue = payments_f["expected_amount_xaf"].sum() if not payments_f.empty and "expected_amount_xaf" in payments_f.columns else 0

collection_rate = total_revenue / expected_revenue if expected_revenue else 0
total_alerts = telemetry_f["alert_count"].sum() if not telemetry_f.empty and "alert_count" in telemetry_f.columns else 0

avg_solar = telemetry_f["avg_solar_output_w"].mean() if not telemetry_f.empty and "avg_solar_output_w" in telemetry_f.columns else 0

c1, c2, c3, c4, c5  = st.columns(5)
c1.metric("Nombre d'Installations", f"{total_installations:,.0f}")
c2.metric("Installations Actives", f"{active_installations:,.0f}")
c3.metric("CA SolarMboa", f"{total_revenue:,.0f} XAF")
c4.metric("Taux de Recouvrement", f"{collection_rate:.1%}")
c5.metric("Nbre d'Alertes", f"{total_alerts:,.0f}")

# Insights
i1, i2 = st.columns(2)

with i1:
    if not payments_f.empty and "region_name" in payments_f.columns:
        top = payments_f.groupby("region_name", as_index=False).agg(revenus=("amount_xaf", "sum")).sort_values("revenus", ascending=False).head(1)
        if not top.empty:
            st.markdown(f"<div class='insight-box' style='margin-verticale: '20px'' ><b>Région la plus rentable</b><br>{top.iloc[0]['region_name']} génère <b>{top.iloc[0]['revenus']:,.0f} XAF</b>.</div>", unsafe_allow_html=True)
            
with i2:
    if not telemetry_f.empty and "region_name" in telemetry_f.columns:
        risk = telemetry_f.groupby("region_name", as_index=False).agg(alertes=("alert_count", "sum")).sort_values("alertes", ascending=False).head(1)
        if not risk.empty:
            st.markdown(f'<div class="insight-box"><b>Région sensible</b><br>{risk.iloc[0]["region_name"]} concentre <b>{risk.iloc[0]["alertes"]:,.0f}</b> alertes.</div>', unsafe_allow_html=True)


    
# Revenus
st.markdown('<div class="section-title">Revenus et recouvrement</div>', unsafe_allow_html=True)
r1, r2 = st.columns(2)
with r1:
    if not payments_f.empty and "region_name" in payments_f.columns:
        data = payments_f.groupby("region_name", as_index=False).agg(total_revenue_xaf=("amount_xaf", "sum")).sort_values("total_revenue_xaf", ascending=False)
        fig = px.bar(data, x="region_name", y="total_revenue_xaf", title="Revenus par région", labels={"region_name": "Région", "total_revenue_xaf": "Revenus XAF"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de paiement disponible.")
with r2:
    if not payments_f.empty and "contract_plan" in payments_f.columns:
        data = payments_f.groupby("contract_plan", as_index=False).agg(total_revenue_xaf=("amount_xaf", "sum")).sort_values("total_revenue_xaf", ascending=False)
        fig = px.pie(data, names="contract_plan", values="total_revenue_xaf", title="Revenus par plan tarifaire", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de plan disponible.")

p1, p2 = st.columns(2)
with p1:
    if not payments_filtered.empty and "payment_method" in payments_filtered.columns:
        payment_channel = (
            payments_filtered.groupby("payment_method", as_index=False)
            .agg(total_revenue_xaf=("amount_xaf", "sum"))
            .sort_values("total_revenue_xaf", ascending=False)
        )

        fig = px.pie(
            payment_channel,
            names="payment_method",
            values="total_revenue_xaf",
            title="Répartition du chiffre d'affaires par canal de paiement",
            hole=0.45,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de canal de paiement disponible.")      

with p2:    
    if (
    not payments_filtered.empty
    and "contract_plan" in payments_filtered.columns
    and "amount_xaf" in payments_filtered.columns
    and "expected_amount_xaf" in payments_filtered.columns):
        recovery_plan = (
            payments_filtered.groupby("contract_plan", as_index=False)
            .agg(
                ca_reel=("amount_xaf", "sum"),
                ca_attendu=("expected_amount_xaf", "sum"),
            )
        )

        recovery_plan["taux_recouvrement_pct"] = (
            recovery_plan["ca_reel"] / recovery_plan["ca_attendu"] * 100
        )

        recovery_plan = recovery_plan.sort_values(
            "taux_recouvrement_pct",
            ascending=False,
        )
        
        fig = px.pie(
            recovery_plan,
            names="contract_plan",
            values="taux_recouvrement_pct",
            title="Taux de recouvrement par plan tarifaire",
            hole=0.45,
            labels={"contract_plan": "Plan tarifaire", "taux_recouvrement_pct": "Taux de recouvrement (%)"},    
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Impossible d'afficher le taux de recouvrement par plan.")         

      

# Payement
if not payments_f.empty and "full_date" in payments_f.columns:
    data = payments_f.dropna(subset=["full_date"]).groupby("full_date", as_index=False).agg(total_revenue_xaf=("amount_xaf", "sum")).sort_values("full_date")
    fig = px.line(data, x="full_date", y="total_revenue_xaf", title="Évolution du chiffre d'affaires journalier", labels={"full_date": "Date", "total_revenue_xaf": "Revenus XAF"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée de paiement disponible pour l'évolution temporelle.")
        

# Énergie
st.markdown('<div class="section-title">Production solaire et consommation</div>', unsafe_allow_html=True)
e1, e2 = st.columns(2)
with e1:
    if not telemetry_f.empty and "region_name" in telemetry_f.columns:
        data = telemetry_f.groupby("region_name", as_index=False).agg(avg_solar_output_w=("avg_solar_output_w", "mean")).sort_values("avg_solar_output_w", ascending=False)
        fig = px.bar(data, x="region_name", y="avg_solar_output_w", title="Production solaire moyenne par région", labels={"region_name": "Région", "avg_solar_output_w": "Production moyenne W"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de production disponible.")
with e2:
    if not telemetry_f.empty and "region_name" in telemetry_f.columns:
        data = telemetry_f.groupby("region_name", as_index=False).agg(avg_consumption_w=("avg_consumption_w", "mean")).sort_values("avg_consumption_w", ascending=False)
        fig = px.bar(data, x="region_name", y="avg_consumption_w", title="Consommation moyenne par région", labels={"region_name": "Région", "avg_consumption_w": "Consommation moyenne W"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de consommation disponible.")

if not telemetry_f.empty and "full_date" in telemetry_f.columns:
    data = telemetry_f.dropna(subset=["full_date"]).groupby("full_date", as_index=False).agg(avg_solar_output_w=("avg_solar_output_w", "mean")).sort_values("full_date")
    fig = px.line(data, x="full_date", y="avg_solar_output_w", title="Évolution de la production solaire moyenne", labels={"full_date": "Date", "avg_solar_output_w": "Production moyenne W"})
    st.plotly_chart(fig, use_container_width=True)


if (
    not telemetry_filtered.empty
    and "region_name" in telemetry_filtered.columns
    and "avg_solar_output_w" in telemetry_filtered.columns
    and "avg_consumption_w" in telemetry_filtered.columns
):
    energy_balance = (
        telemetry_filtered.groupby("region_name", as_index=False)
        .agg(
            production_moyenne_w=("avg_solar_output_w", "mean"),
            consommation_moyenne_w=("avg_consumption_w", "mean"),
        )
    )

    energy_balance["ecart_production_consommation_w"] = (
        energy_balance["production_moyenne_w"]
        - energy_balance["consommation_moyenne_w"]
    )

    fig = px.bar(
        energy_balance,
        x="region_name",
        y=["production_moyenne_w", "consommation_moyenne_w"],
        barmode="group",
        title="Production solaire vs consommation moyenne par région",
        labels={
            "region_name": "Région",
            "value": "Watts",
            "variable": "Indicateur",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Impossible d'afficher production vs consommation.")

# Parc et alertes
st.markdown('<div class="section-title">Santé du parc et alertes</div>', unsafe_allow_html=True)
o1, o2 = st.columns(2)
with o1:
    if not dim_installation.empty and "status" in dim_installation.columns:
        data = dim_installation.groupby("status", as_index=False).agg(installations=("installation_id", "nunique")).sort_values("installations", ascending=False)
        fig = px.pie(data, names="status", values="installations", title="État du parc d'installations", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
with o2:
    if not telemetry_f.empty and "region_name" in telemetry_f.columns:
        data = telemetry_f.groupby("region_name", as_index=False).agg(total_alerts=("alert_count", "sum")).sort_values("total_alerts", ascending=False)
        fig = px.bar(data, x="region_name", y="total_alerts", title="Alertes par région", labels={"region_name": "Région", "total_alerts": "Nombre d'alertes"})
        st.plotly_chart(fig, use_container_width=True)

# Réseau
st.markdown('<div class="section-title">Réseau de distribution</div>', unsafe_allow_html=True)
if not sales_network.empty and "distributor_name" in sales_network.columns:
    data = sales_network.dropna(subset=["distributor_name"]).groupby("distributor_name", as_index=False).agg(total_relations=("sales_network_key", "count")).sort_values("total_relations", ascending=False).head(10)
    fig = px.bar(data, x="total_relations", y="distributor_name", orientation="h", title="Top 10 distributeurs par volume de relations", labels={"total_relations": "Nombre de relations", "distributor_name": "Distributeur"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée distributeur disponible.")

            
st.markdown('<div class="section-title">Taux de recouvrement par région</div>', unsafe_allow_html=True)

if (
    not payments_filtered.empty
    and "region_name" in payments_filtered.columns
    and "amount_xaf" in payments_filtered.columns
    and "expected_amount_xaf" in payments_filtered.columns
):
    recovery_region = (
        payments_filtered.groupby("region_name", as_index=False)
        .agg(
            ca_reel=("amount_xaf", "sum"),
            ca_attendu=("expected_amount_xaf", "sum"),
        )
    )

    recovery_region["taux_recouvrement"] = (
        recovery_region["ca_reel"] / recovery_region["ca_attendu"]
    )

    fig = px.bar(
        recovery_region,
        x="region_name",
        y=["ca_reel", "ca_attendu"],
        barmode="group",
        title="CA réel vs CA attendu par région",
        labels={
            "region_name": "Région",
            "value": "Montant XAF",
            "variable": "Indicateur",
        },
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Impossible d'afficher le CA réel vs attendu : colonnes manquantes.")    
    
    
# Contrôle
with st.expander("Tables de contrôle du Data Warehouse"):
    tables = {
        "dim_installation": dim_installation,
        "dim_contract_plan": dim_contract_plan,
        "dim_region": dim_region,
        "fact_telemetry_daily": fact_telemetry_daily,
        "fact_payments": fact_payments,
        "fact_sales_network": fact_sales_network,
    }
    table_choice = st.selectbox("Choisir une table", list(tables.keys()))
    st.dataframe(tables[table_choice].head(100), use_container_width=True)
    