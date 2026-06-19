"""
Rapport automatique des anomalies a detecter chaque mois.
5 types d'anomalies a implementer.
"""

from datetime import datetime, timedelta
from solarmboa.database import get_db

col = get_db()["installations"]
seuil_paiement = datetime.utcnow() - timedelta(days=45)
seuil_maintenance = datetime.utcnow() - timedelta(days=7)

pipelines = {
    "installations_sans_gps": [
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
                "location.city": 1,
                "location.region": 1,
            }
        },
    ],

    "maintenance_plus_3_correctives": [
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
                "corrective_count": 1,
                "status": 1,
            }
        },
    ],

    "standard_vers_premium": [
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
            }
        },
    ],

    "actives_sans_paiement_recent": [
        {
            "$match": {
                "status": "active",
                "metrics.last_payment_date": {"$lt": seuil_paiement},
            }
        },
        {
            "$project": {
                "_id": 0,
                "installation_id": 1,
                "client_name": 1,
                "metrics.last_payment_date": 1,
                "contract.monthly_xaf": 1,
            }
        },
    ],

    "health_centers_sans_sla": [
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
    ],
}

if __name__ == '__main__':
    print("\n=== RAPPORT D'ANOMALIES MONGODB ===")
    
    for name, pipeline in pipelines.items():
        
        result = list(col.aggregate(pipeline))
        print(f"\n{name}: {len(result)} résultat(s)")
        
        for doc in result[:5]:
            print(doc)