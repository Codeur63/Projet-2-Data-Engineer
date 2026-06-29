from solarmboa.database import get_db


db = get_db()
col = db["installations"]


def main() -> None:
    query = {
        "client_type": "health_center",
        "status": "active",
        "$or": [
            {"facility.has_cold_chain": False},
            {"facility.has_cold_chain": {"$exists": False}},
            {"facility.has_cold_chain": None},
        ],
    }

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$location.region",
                "health_centers_without_cold_chain": {"$sum": 1},
                "current_monthly_revenue_xaf": {
                    "$sum": "$contract.monthly_xaf"
                },
            }
        },
        {
            "$addFields": {
                "upgrade_investment_xaf": {
                    "$multiply": [
                        "$health_centers_without_cold_chain",
                        2_500_000,
                    ]
                },
                "additional_monthly_revenue_xaf": {
                    "$multiply": [
                        "$health_centers_without_cold_chain",
                        35_000,
                    ]
                },
            }
        },
        {
            "$addFields": {
                "roi_months": {
                    "$cond": [
                        {"$gt": ["$additional_monthly_revenue_xaf", 0]},
                        {
                            "$round": [
                                {
                                    "$divide": [
                                        "$upgrade_investment_xaf",
                                        "$additional_monthly_revenue_xaf",
                                    ]
                                },
                                2,
                            ]
                        },
                        None,
                    ]
                }
            }
        },
        {"$sort": {"health_centers_without_cold_chain": -1}},
    ]

    result = list(col.aggregate(pipeline))

    print("\n===== Q3 — CENTRES DE SANTÉ SANS CHAÎNE DU FROID =====")
    for row in result:
        print(row)


if __name__ == "__main__":
    main()