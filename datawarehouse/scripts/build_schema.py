from pathlib import Path
import json
from dotenv import load_dotenv
import os

import pandas as pd

load_dotenv()

INSTALLATIONSJSON = os.getenv("INSTALLATION_JSON")
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"

TELEMETRY_CSV = os.getenv("SENSOR_TELEMETRY")
PAYMENTS_CSV = os.getenv("PAYMENTS")
DISRIBUTOR = os.getenv("DISTRIBUTOR")
TECHNICIANS = os.getenv("TECHNICIANS")
GRAPH = os.getenv("GRAPH")
WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)


def load_sources():
    with open(INSTALLATIONSJSON, "r", encoding="utf-8") as f:
        installations = json.load(f)

    df_installations = pd.DataFrame(installations)
    df_telemetry = pd.read_csv(TELEMETRY_CSV)
    df_payments = pd.read_csv(PAYMENTS_CSV)
    df_distributors = pd.read_csv(DISRIBUTOR)
    df_technicians = pd.read_csv(TECHNICIANS)
    df_graph = pd.read_csv(GRAPH)

    return {
        "installations": df_installations,
        "telemetry": df_telemetry,
        "payments": df_payments,
        "distributors": df_distributors,
        "technicians": df_technicians,
        "graph": df_graph,
    }


def build_dim_contract_plan(df_installations, df_payments):
    
    plan_pricing = df_installations[['installation_id', 'tariff_plan']].merge(
        df_payments[['installation_id', 'amount_xaf', 'payment_date', 'status', 'channel', 'operator_code']],
        on='installation_id',
        how='inner' # Uniquement ceux qui ont un payement
    )

    plan_prices = plan_pricing.groupby('tariff_plan')['amount_xaf'].median().reset_index()

    dim_contract_plan = plan_prices.rename(columns={
        'tariff_plan': 'plan_name', 
        'amount_xaf': 'monthly_price_xaf'
    })
       
    dim_contract_plan.insert(0, "contract_plan_key", range(1, len(dim_contract_plan) + 1))
    
    return dim_contract_plan

def build_dim_contract(df_installations, df_payments):
    plan_pricing = df_installations[['installation_id', 'tariff_plan']].merge(
        df_payments[['installation_id', 'amount_xaf', 'payment_date', 'status', 'channel', 'operator_code']],
        on='installation_id',
        how='inner' # Uniquement ceux qui ont un payement
    )
    
    dim_contract = plan_pricing.rename(columns={
        'tariff_plan':'contract',
        'amount_xaf':'month_price_xaf'
    })
    
    dim_contract.insert(0, "contract_key", range(1, len(dim_contract)+1))
    
    return dim_contract


def build_dim_region(df_installations, df_distributors, df_technicians):
    regions = pd.concat(
        [
            df_installations["region"],
            df_distributors["region"],
            df_technicians["region"],
        ],
        ignore_index=True,
    ).dropna().drop_duplicates().sort_values()

    dim_region = pd.DataFrame({"region_name": regions})
    dim_region.insert(0, "region_key", range(1, len(dim_region) + 1))

    return dim_region


def build_dim_city(df_installations):
    city = df_installations['city'].dropna().drop_duplicates().sort_values()
    
    dim_city = pd.DataFrame({'city':city}) 
    dim_city.insert(0,'city_key', range(1, len(dim_city)+1))
    return dim_city



def build_dim_type(df_installation):
    client_type = df_installation['client_type'].dropna().drop_duplicates().sort_values()
    dim_type = pd.DataFrame({'client_type':client_type})
    
    dim_type.insert(0, 'type_key', range(1,len(dim_type)+1))    
    return dim_type


def build_dim_client(df_installation, dim_region, dim_type):
    dim_client = df_installation[['client_name','client_type','region']].merge(
        dim_region, 
        left_on="region", 
        right_on='region_name', 
        how='left'
    )
    
    dim_client = dim_client.merge(
        dim_type,
        left_on='client_type',
        right_on='client_type',
        how='left'
    )
         
    dim_client.insert(0, "client_key", range(1, len(dim_client) + 1))
    
    return dim_client[
        [
         "client_key",   
        'client_name',
        'type_key',
        'region_key'
        ]
        ]

def build_dim_relation(df_graph):
    relation = df_graph['relation'].dropna().drop_duplicates().sort_values()

    dim_relation = pd.DataFrame({'relation':relation}) 
    dim_relation.insert(0, 'relation_key', range(1,len(dim_relation)+1))    
    
    return dim_relation



def build_dim_installation(df_installations, dim_region, dim_contract_plan):
    dim = df_installations[
        [
            "installation_id",
            "client_name",
            "client_type",
            "status",
            "region",
            "city",
            "tariff_plan",
            "install_date",
            "panel_capacity_wp",
            "battery_capacity_wh",
            "num_appliances",
        ]
    ].copy()

    dim = dim.merge(
        dim_region,
        left_on="region",
        right_on="region_name",
        how="left",
    )

    dim = dim.rename(columns={"tariff_plan": "contract_plan"})
    
    dim = dim.merge(
        dim_contract_plan[["contract_plan_key", "plan_name", "monthly_price_xaf"]],
        left_on="contract_plan",
        right_on="plan_name",
        how="left",
    )
    
    
    missing_plans = dim["contract_plan_key"].isna().sum()
    
    if missing_plans > 0:
        print(
            f"Attention : {missing_plans} installations ont un plan tarifaire inconnu."
        )

        rejected_path = WAREHOUSE_DIR / "rejected_installations_unknown_plan.csv"
        dim[dim["contract_plan_key"].isna()].to_csv(rejected_path, index=False)

        print(f"Installations avec plan inconnu exportées dans : {rejected_path}")
    
    dim.insert(0, "installation_key", range(1, len(dim) + 1))

    return dim[
        [
            "installation_key",
            "installation_id",
            "client_name",
            "client_type",
            "status",
            "region_key",
            "city",
            "contract_plan_key",
            "contract_plan",
            "monthly_price_xaf",
            "install_date",
            "panel_capacity_wp",
            "battery_capacity_wh",
            "num_appliances"
        ]
    ]


def build_dim_distributor(df_distributors, dim_region):
    dim = df_distributors.copy()

    dim = dim.merge(
        dim_region,
        left_on="region",
        right_on="region_name",
        how="left",
    )

    dim = dim.rename(
        columns={
            "id": "distributor_id",
            "name": "distributor_name",
            "since": "since_date",
        }
    )

    dim.insert(0, "distributor_key", range(1, len(dim) + 1))

    return dim[
        [
            "distributor_key",
            "distributor_id",
            "distributor_name",
            "region_key",
            "since_date",
        ]
    ]


def build_dim_technician(df_technicians, dim_region):
    dim = df_technicians.copy()

    dim = dim.merge(
        dim_region,
        left_on="region",
        right_on="region_name",
        how="left",
    )

    dim = dim.rename(
        columns={
            "id": "technician_id",
            "name": "technician_name",
        }
    )

    dim.insert(0, "technician_key", range(1, len(dim) + 1))

    return dim[
        [
            "technician_key",
            "technician_id",
            "technician_name",
            "region_key",
            "phone",
            "certified",
        ]
    ]


def build_dim_date(df_telemetry, df_payments, df_installations):
    dates = []

    if "timestamp" in df_telemetry.columns:
        dates.append(pd.to_datetime(df_telemetry["timestamp"], errors="coerce").dt.date)

    if "payment_date" in df_payments.columns:
        dates.append(pd.to_datetime(df_payments["payment_date"], errors="coerce").dt.date)

    if "install_date" in df_installations.columns:
        dates.append(pd.to_datetime(df_installations["install_date"], errors="coerce").dt.date)

    all_dates = pd.concat(dates, ignore_index=True).dropna().drop_duplicates()
    all_dates = pd.Series(sorted(all_dates))

    dim_date = pd.DataFrame({"full_date": pd.to_datetime(all_dates)})

    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["day_name"] = dim_date["full_date"].dt.day_name()
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["is_weekend"] = dim_date["full_date"].dt.weekday >= 5

    return dim_date[
        [
            "date_key",
            "full_date",
            "day",
            "month",
            "quarter",
            "year",
            "day_name",
            "month_name",
            "is_weekend",
        ]
    ]



def build_dim_alert(df_telemetry):
    alerts = (
        df_telemetry["alert_code"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    dim_alert = pd.DataFrame({"alert_code": alerts})
    dim_alert.insert(0, "alert_key", range(1, len(dim_alert) + 1))

    dim_alert["alert_category"] = "sensor"

    return dim_alert


def build_fact_telemetry_daily(df_telemetry, dim_installation, dim_date, dim_alert):
    df = df_telemetry.copy()

    df["date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.date
    df["date_key"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d").astype(int)

    grouped = (
        df.groupby(["installation_id", "date_key"], as_index=False)
        .agg(
            avg_solar_output_w=("solar_output_w", "mean"),
            max_solar_output_w=("solar_output_w", "max"),
            avg_battery_level_pct=("battery_level_pct", "mean"),
            min_battery_level_pct=("battery_level_pct", "min"),
            avg_consumption_w=("consumption_w", "mean"),
            alert_count=("alert_code", lambda x: x.notna().sum()),
            daily_alerts=("alert_code", lambda x: ", ".join(sorted(x.dropna().unique())) if x.notna().any() else None)
        )
    )

    fact = grouped.merge(
        dim_installation[["installation_key", "installation_id"]],
        on="installation_id",
        how="left",
    )

    fact.insert(0, "telemetry_key", range(1, len(fact) + 1))

    return fact[
        [
            "telemetry_key",
            "date_key",
            "installation_key",
            "avg_solar_output_w",
            "max_solar_output_w",
            "avg_battery_level_pct",
            "min_battery_level_pct",
            "avg_consumption_w",
            "alert_count",
            "daily_alerts"
        ]
    ]


def build_fact_payments(df_payments, dim_installation):
    df = df_payments.copy()

    date_col = "payment_date"
    amount_col = "amount_xaf"
    status_col = "status"
    method_col = "channel"

    df["payment_date_parsed"] = pd.to_datetime(df[date_col], errors="coerce")

    invalid_dates = df["payment_date_parsed"].isna().sum()

    if invalid_dates > 0:
        print(
            f"Attention : {invalid_dates} paiements ont une date invalide "
            f"et seront ignorés."
        )

        rejected_path = WAREHOUSE_DIR / "rejected_payments_invalid_dates.csv"
        df[df["payment_date_parsed"].isna()].to_csv(rejected_path, index=False)

        print(f"Paiements rejetés exportés dans : {rejected_path}")

    df = df.dropna(subset=["payment_date_parsed"])

    df["date_key"] = df["payment_date_parsed"].dt.strftime("%Y%m%d").astype(int)

    df["installation_id"] = pd.to_numeric(
        df["installation_id"],
        errors="coerce"
    ).astype("Int64")

    df = df.dropna(subset=["installation_id"])

    fact = df.merge(
        dim_installation[
            [
                "installation_key",
                "installation_id",
                "contract_plan_key",
                "monthly_price_xaf",
            ]
        ],
        on="installation_id",
        how="left",
    )

    missing_installations = fact["installation_key"].isna().sum()

    if missing_installations > 0:
        print(
            f"Attention : {missing_installations} paiements ne correspondent "
            f"à aucune installation connue."
        )

        rejected_path = WAREHOUSE_DIR / "rejected_payments_missing_installations.csv"
        fact[fact["installation_key"].isna()].to_csv(rejected_path, index=False)

        print(f"Paiements rejetés exportés dans : {rejected_path}")

    fact = fact.dropna(subset=["installation_key"])

    fact["installation_key"] = fact["installation_key"].astype("Int64")
    fact["contract_plan_key"] = fact["contract_plan_key"].astype("Int64")

    fact["payment_gap_xaf"] = fact[amount_col] - fact["monthly_price_xaf"]

    fact.insert(0, "payment_key", range(1, len(fact) + 1))

    return pd.DataFrame(
        {
            "payment_key": fact["payment_key"],
            "date_key": fact["date_key"],
            "installation_key": fact["installation_key"],
            "installation_id": fact["installation_id"],
            "contract_plan_key": fact["contract_plan_key"],
            "payment_id": fact["payment_id"],
            "amount_xaf": fact[amount_col],
            "expected_amount_xaf": fact["monthly_price_xaf"],
            "payment_gap_xaf": fact["payment_gap_xaf"],
            "payment_status": fact[status_col],
            "payment_method": fact[method_col],
        }
    )



def build_fact_sales_network(df_graph, dim_installation, dim_distributor, dim_technician, dim_relation):
    df = df_graph.copy()
    df["target_id_int"] = pd.to_numeric(df["target_id"], errors="coerce")

    fact = df.merge(
        dim_installation[["installation_key", "installation_id"]],
        left_on="target_id_int",
        right_on="installation_id",
        how="left",
    )

    fact = fact.merge(
        dim_distributor[["distributor_key", "distributor_id"]],
        left_on="source_id",
        right_on="distributor_id",
        how="left",
    )
    
    fact = fact.merge(
        dim_relation,
        left_on="relation",
        right_on='relation',
        how='left'
    )

    fact = fact.merge(
        dim_technician[["technician_key", "technician_id"]],
        left_on="source_id",
        right_on="technician_id",
        how="left",
    )

    fact.insert(0, "sales_network_key", range(1, len(fact) + 1))

    fact["date_key"] = pd.to_datetime(fact["date"], errors="coerce").dt.strftime("%Y%m%d")
    fact["date_key"] = pd.to_numeric(fact["date_key"], errors="coerce").astype("Int64")

    return fact[
        [
            "sales_network_key",
            "date_key",
            "installation_key",
            "distributor_key",
            "technician_key",
            "relation_key",
            "weight",
        ]
    ].rename(columns={"weight": "relation_weight"})


def export_table(df, name):
    path = WAREHOUSE_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"{name}: {len(df):,} lignes -> {path}")


def main():
    sources = load_sources()

    df_installations = sources["installations"]
    df_telemetry = sources["telemetry"]
    df_payments = sources["payments"]
    df_distributors = sources["distributors"]
    df_technicians = sources["technicians"]
    df_graph = sources["graph"]

    dim_region = build_dim_region(df_installations, df_distributors, df_technicians)
    dim_date = build_dim_date(df_telemetry, df_payments, df_installations)
    dim_contract_plan = build_dim_contract_plan(df_installations, df_payments)
    dim_contract = build_dim_contract(df_installations,df_payments)
    dim_alert = build_dim_alert(df_telemetry)
    dim_city = build_dim_city(df_installations)
    dim_type = build_dim_type(df_installations)
    dim_relation = build_dim_relation(df_graph)
    dim_client = build_dim_client(df_installations, dim_region, dim_type)
    dim_installation = build_dim_installation(df_installations, dim_region, dim_contract_plan)
    dim_distributor = build_dim_distributor(df_distributors, dim_region)
    dim_technician = build_dim_technician(df_technicians, dim_region)

    fact_telemetry_daily = build_fact_telemetry_daily(
        df_telemetry,
        dim_installation,
        dim_date,
        dim_alert,
    )

    fact_payments = build_fact_payments(
        df_payments,
        dim_installation,
    )

    fact_sales_network = build_fact_sales_network(
        df_graph,
        dim_installation,
        dim_distributor,
        dim_technician,
        dim_relation
    )

    tables = {
        "dim_region": dim_region,
        "dim_contract_plan": dim_contract_plan,
        "dim_contract": dim_contract, 
        "dim_date": dim_date,
        "dim_alert": dim_alert,
        "dim_city": dim_city,
        "dim_type": dim_type,
        "dim_client": dim_client,
        "dim_relation": dim_relation,
        "dim_installation": dim_installation,
        "dim_distributor": dim_distributor,
        "dim_technician": dim_technician,
        "fact_telemetry_daily": fact_telemetry_daily,
        "fact_payments": fact_payments,
        "fact_sales_network": fact_sales_network,
    }

    for name, df in tables.items():
        export_table(df, name)

    print("\nData Warehouse construit avec succès.")


if __name__ == "__main__":
    main()