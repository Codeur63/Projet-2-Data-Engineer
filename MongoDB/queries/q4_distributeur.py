from solarmboa.database import get_db


db = get_db()
col = db["installations"]


def main() -> None:
    pipeline = [
        {
            "$match": {
                "status": "active",
                "contract.monthly_xaf": {"$gt": 0},
                "distributor_id": {"$exists": True},
            }
        },
        {
            "$group": {
                "_id": "$distributor_id",
                "active_installations": {"$sum": 1},
                "monthly_revenue_xaf": {"$sum": "$contract.monthly_xaf"},
                "avg_revenue_xaf": {"$avg": "$contract.monthly_xaf"},
            }
        },
        {"$sort": {"monthly_revenue_xaf": -1}},
        {"$limit": 10},
    ]

    results = list(col.aggregate(pipeline))

    print("\n===== Q4 — TOP 10 DISTRIBUTEURS PAR CA MENSUEL =====")
    for row in results:
        print(
            f"Distributeur {row['_id']} | "
            f"installations actives: {row['active_installations']} | "
            f"CA mensuel: {row['monthly_revenue_xaf']:,.0f} XAF | "
            f"CA moyen: {row['avg_revenue_xaf']:,.0f} XAF"
        )


if __name__ == "__main__":
    main()