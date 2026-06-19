"""
Cree tous les index MongoDB sur l'installation locale.
Idempotent — safe a executer plusieurs fois.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, TEXT
from solarmboa.database import get_db


def create_all_indexes():
    db = get_db()
    col = db["installations"]
    index_specs = [
        # 1. Cle primaire metier — unique, O(log n)
        (
            [("installation_id", ASCENDING)],
            {"unique": True, "name": "idx_installation_id_unique"},
        ),
        # 2. Requetes dashboard — region + statut (ESR)
        (
            [("location.region", ASCENDING), ("status", ASCENDING)],
            {"name": "idx_region_status"},
        ),
        # 3. Segmentation type x statut x plan
        (
            [
                ("client_type", ASCENDING),
                ("status", ASCENDING),
                ("contract.plan", ASCENDING),
            ],
            {"name": "idx_type_status_plan"},
        ),
        # 4. Geospatial — techniciens terrain
        ([("location.gps", GEOSPHERE)], {"name": "idx_gps_2dsphere", "sparse": True}),
        # 5. CA mensuel — actifs seulement (index partiel)
        (
            [("contract.monthly_xaf", DESCENDING)],
            {"partialFilterExpression": {"status": "active"}, "name": "idx_ca_actives"},
        ),
        # 6. Distributeur
        (
            [("distributor_id", ASCENDING), ("status", ASCENDING)],
            {"name": "idx_distributor_status"},
        ),
        # 7. Dernier paiement — detection churn
        (
            [("metrics.last_payment_date", ASCENDING)],
            {
                "partialFilterExpression": {"status": "active"},
                "name": "idx_last_payment_active",
            },
        ),
        # 8. Full-text sur noms clients
        (
            [("client_name", TEXT), ("location.city", TEXT)],
            {
                "weights": {"client_name": 10, "location.city": 5},
                "default_language": "french",
                "name": "idx_text_name_city",
            },
        ),
    ]
    print("Creation des index...")
    for keys, opts in index_specs:
        col.create_index(keys, **opts)
        print(f' OK : {opts["name"]}')
    print(f"Total : {len(index_specs)} index crees.")
    print()
    print("Index existants :")
    for idx in col.index_information().keys():
        print(f" - {idx}")


if __name__ == "__main__":
    create_all_indexes()
