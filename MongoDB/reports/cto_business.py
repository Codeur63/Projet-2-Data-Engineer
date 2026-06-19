"""
Rapport exécutif MongoDB pour le CTO SolarMboa.

Objectif :
- Consolider les KPI business
- Détecter les anomalies opérationnelles
- Produire une sortie lisible pour la soutenance
"""

from datetime import datetime, timedelta
from pprint import pprint

from solarmboa.database import get_db


db = get_db()
col = db["installations"]


def count_installations() -> dict:
    return {
        "total": col.count_documents({}),
        "active": col.count_documents({"status": "active"}),
        "maintenance": col.count_documents({"status": "maintenance"}),
        "suspended": col.count_documents({"status": "suspended"}),
        "churned": col.count_documents({"status": "churned"}),
    }


def monthly_revenue_active() -> float:
    pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": None,
                "total_ca": {"$sum": "$contract.monthly_xaf"},
            }
        },
    ]

    result = list(col.aggregate(pipeline))
    return result[0]["total_ca"] if result else 0


def revenue_by_region() -> list[dict]:
    pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$location.region",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
    ]

    return list(col.aggregate(pipeline))


def revenue_by_plan() -> list[dict]:
    pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$contract.plan",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
    ]

    return list(col.aggregate(pipeline))


def top_distributors(limit: int = 10) -> list[dict]:
    pipeline = [
        {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
        {
            "$group": {
                "_id": "$distributor_id",
                "installations": {"$sum": 1},
                "ca_total": {"$sum": "$contract.monthly_xaf"},
                "ca_moyen": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"ca_total": -1}},
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def installations_without_gps(limit: int = 10) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"location.gps": {"$exists": False}},
                    {"location.gps.coordinates.0": None},
                    {"location.gps.coordinates.1": None},
                    {"location.gps_available": False},
                ]
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "client_type": 1,
                "location.city": 1,
                "location.region": 1,
            }
        },
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def installations_with_many_correctives(limit: int = 10) -> list[dict]:
    pipeline = [
        {
            "$addFields": {
                "corrective_count": {
                    "$size": {
                        "$filter": {
                            "input": "$maintenance_history",
                            "as": "m",
                            "cond": {"$eq": ["$$m.type", "corrective"]},
                        }
                    }
                }
            }
        },
        {"$match": {"corrective_count": {"$gt": 3}}},
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "status": 1,
                "corrective_count": 1,
                "location.region": 1,
            }
        },
        {"$sort": {"corrective_count": -1}},
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def standard_to_premium(limit: int = 10) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "contract.history": {
                    "$elemMatch": {
                        "from_plan": "Standard",
                        "to_plan": "Premium",
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "contract.plan": 1,
                "contract.history": 1,
                "contract.monthly_xaf": 1,
            }
        },
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def old_payment_risk(limit: int = 10) -> list[dict]:
    threshold = datetime.utcnow() - timedelta(days=45)

    pipeline = [
        {
            "$match": {
                "status": "active",
                "metrics.last_payment_date": {"$lt": threshold},
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "metrics.last_payment_date": 1,
                "contract.monthly_xaf": 1,
                "location.region": 1,
            }
        },
        {"$sort": {"metrics.last_payment_date": 1}},
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def health_centers_without_sla(limit: int = 10) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "client_type": "health_center",
                "$or": [
                    {"sla_uptime_pct": None},
                    {"sla_uptime_pct": {"$lt": 95}},
                ],
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "location.region": 1,
                "sla_uptime_pct": 1,
            }
        },
        {"$limit": limit},
    ]

    return list(col.aggregate(pipeline))


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_rows(rows: list[dict], max_rows: int = 10):
    if not rows:
        print("Aucun résultat.")
        return

    for row in rows[:max_rows]:
        pprint(row, sort_dicts=False)


def main():
    print_section("SOLARMBOA — RAPPORT CTO MONGODB")
    print(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    counts = count_installations()
    ca_total = monthly_revenue_active()

    print_section("1. KPI GLOBAUX")
    print(f"Installations totales      : {counts['total']:,}")
    print(f"Installations actives      : {counts['active']:,}")
    print(f"En maintenance             : {counts['maintenance']:,}")
    print(f"Suspendues                 : {counts['suspended']:,}")
    print(f"Churned                    : {counts['churned']:,}")
    print(f"CA mensuel actif estimé    : {ca_total:,.0f} XAF")

    print_section("2. CA MENSUEL PAR RÉGION")
    print_rows(revenue_by_region())

    print_section("3. CA MENSUEL PAR PLAN TARIFAIRE")
    print_rows(revenue_by_plan())

    print_section("4. TOP 10 DISTRIBUTEURS PAR CA")
    print_rows(top_distributors())

    print_section("5. ANOMALIES — INSTALLATIONS SANS GPS")
    print_rows(installations_without_gps())

    print_section("6. ANOMALIES — PLUS DE 3 MAINTENANCES CORRECTIVES")
    print_rows(installations_with_many_correctives())

    print_section("7. OPPORTUNITÉ — PASSAGE STANDARD VERS PREMIUM")
    print_rows(standard_to_premium())

    print_section("8. RISQUE — PAIEMENT ANCIEN")
    print_rows(old_payment_risk())

    print_section("9. SANTÉ — CENTRES SANS SLA OU SLA FAIBLE")
    print_rows(health_centers_without_sla())

    print_section("CONCLUSION CTO")
    print(
        "MongoDB permet de consolider les profils d'installations, "
        "les contrats, la localisation, la maintenance et les indicateurs business. "
        "Les agrégations produisent des KPI directement exploitables pour le pilotage "
        "opérationnel et commercial de SolarMboa."
    )


if __name__ == "__main__":
    main()