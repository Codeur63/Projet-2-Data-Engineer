from datetime import datetime, timedelta

from solarmboa.database import get_db


db = get_db()
col = db["installations"]


def main() -> None:
    threshold_date = datetime.utcnow() - timedelta(days=45)

    query = {
        "status": "active",
        "$or": [
            {"metrics.last_payment_date": {"$lt": threshold_date}},
            {"metrics.last_payment_date": {"$exists": False}},
            {"metrics.last_payment_date": None},
        ],
    }

    projection = {
        "_id": 0,
        "installation_id": 1,
        "client_name": 1,
        "client_type": 1,
        "location.region": 1,
        "contract.plan": 1,
        "contract.monthly_xaf": 1,
        "metrics.last_payment_date": 1,
    }

    results = list(
        col.find(query, projection)
        .sort("metrics.last_payment_date", 1)
        .limit(20)
    )

    total_risk = col.count_documents(query)

    ca_risk_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$location.region",
                "installations_at_risk": {"$sum": 1},
                "monthly_revenue_at_risk_xaf": {
                    "$sum": "$contract.monthly_xaf"
                },
            }
        },
        {"$sort": {"monthly_revenue_at_risk_xaf": -1}},
    ]

    risk_by_region = list(col.aggregate(ca_risk_pipeline))

    print("\n===== Q2 — CHURN RISK / NON-PAIEMENT =====")
    print(f"Date seuil: {threshold_date}")
    print(f"Installations à risque: {total_risk}")

    print("\n--- Top 20 installations à risque ---")
    for item in results:
        print(item)

    print("\n--- CA mensuel à risque par région ---")
    for row in risk_by_region:
        print(row)


if __name__ == "__main__":
    main()