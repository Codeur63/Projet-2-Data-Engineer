"""Mesure l'impact des index sur les requetes de reference."""

import time
import datetime
from solarmboa.database import get_db
from create_indexes import create_all_indexes

REQUETES = [
    {
        "id": "R1",
        "desc": "Dashboard Littoral actifs",
        "filter": {"location.region": "Littoral", "status": "active"},
        "proj": {"installation_id": 1, "client_name": 1, "_id": 0},
    },
    {
        "id": "R2",
        "desc": "Facturation Premium >= 20 000 XAF",
        "filter": {"contract.plan": "Premium", "contract.monthly_xaf": {"$gte": 20000}},
        "proj": {"installation_id": 1, "contract.monthly_xaf": 1, "_id": 0},
    },
    {
        "id": "R3",
        "desc": "Distributeur 7 actifs",
        "filter": {"distributor_id": 7, "status": "active"},
        "proj": {"installation_id": 1, "_id": 0},
    },
    {
        "id": "R4",
        "desc": "Churn risk — paiement ancien",
        "filter": {
            "status": "active",
            "metrics.last_payment_date": {
                "$lt": datetime.datetime(2025, 9, 1)
            },
        },
        "proj": {"installation_id": 1, "metrics.last_payment_date": 1, "_id": 0},
    },
]


def mesurer(col, filtre, proj, n=20):
    durees = []
    for _ in range(n):
        t0 = time.perf_counter()
        list(col.find(filtre, proj))
        durees.append((time.perf_counter() - t0) * 1000)
    durees.sort()
    return durees[n // 2]


def analyser_plan(col, filtre):
    try:
        plan = col.find(filtre).explain(verbosity="executionStats")
    except TypeError:
        commande_recherche = {"find": col.name, "filter": filtre}
        plan = col.database.command("explain", commande_recherche, verbosity="executionStats")
        
    return {
        "stage": plan["queryPlanner"]["winningPlan"].get("stage", "?"),
        "docs": plan["executionStats"]["totalDocsExamined"],
        "ms": plan["executionStats"]["executionTimeMillis"],
    }


col = get_db()["installations"]

print("Phase 1 — Suppression de tous les index (sauf _id)...")
col.drop_indexes()
print("Suppression Réussi ... ")

resultats = []

for rq in REQUETES:
    plan = analyser_plan(col, rq["filter"])
    ms = mesurer(col, rq["filter"], rq["proj"])    
    resultats.append(
        {"id": rq["id"], "desc": rq["desc"], "ms_avant": ms, "plan_avant": plan}
    )
    print(f"{rq['id']} SANS INDEX : {ms:.1f} ms ({plan['stage']}) docs={plan['docs']}")


print()
print("Phase 2 — Creation des index...")


create_all_indexes()
print()

print(
    f"{'ID':4} {'Description':30} {'Sans (ms)':12} {'Avec (ms)':12} {'Gain':8} {'Stage avant':12} {'Stage apres'}"
)

print("-" * 90)

for i, rq in enumerate(REQUETES):
    plan = analyser_plan(col, rq["filter"])
    ms = mesurer(col, rq["filter"], rq["proj"])
    avant = resultats[i]["ms_avant"]
    gain = avant / ms if ms > 0 else 999
    print(
        f"{rq['id']:4} {rq['desc']:30} {avant:12.1f} {ms:12.1f} x{gain:7.1f} {resultats[i]['plan_avant']['stage']:12} {plan['stage']} docs={plan['docs']}"
    )
