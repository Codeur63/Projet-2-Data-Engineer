from solarmboa.database import get_db

col = get_db()["installations"]

# Pipeline $facet : 4 analyses en 1 seule requete
# Facette 1 : CA mensuel par region x type de client
# Facette 2 : Distribution des plans tarifaires (count + avg CA + total)
# Facette 3 : Top 10 distributions par CA total
# Facette 4 : Outliers CA > P90 (liste des 10 plus gros contrats)

pipeline = [
    {"$match": {"status": "active", "contract.monthly_xaf": {"$gt": 0}}},
    {
        "$facet": {
            "by_region_type": [
                {
                    "$group": {
                        "_id": {"region": "$location.region", "type": "$client_type"},
                        "nb": {"$sum": 1},
                        "avg": {"$avg": "$contract.monthly_xaf"},
                        "total": {"$sum": "$contract.monthly_xaf"},
                    }
                },
                {"$sort": {"total": -1}},
            ],
            "by_plan": [
                {
                    "$group": {
                        "_id": "$contract.plan",
                        "nb": {"$sum": 1},
                        "avg_ca": {"$avg": "$contract.monthly_xaf"},
                        "total_ca": {"$sum": "$contract.monthly_xaf"},
                    }
                },
                {"$sort": {"total_ca": -1}},
            ],
            "top_distributors": [
                {
                    "$group": {
                        "_id": "$distributor_id",
                        "nb_installations": {"$sum": 1},
                        "total_ca": {"$sum": "$contract.monthly_xaf"},
                        "avg_ca": {"$avg": "$contract.monthly_xaf"},
                    }
                },
                {"$sort": {"total_ca": -1}},
                {"$limit": 20},
            ],
            "outliers_ca": [
            {"$sort": {"contract.monthly_xaf": -1}},
            {"$limit": 50},
            {
                "$project": {
                    "_id": 0,
                    "installation_id": 1,
                    "client_name": 1,
                    "client_type": 1,
                    # "location.region": 1,
                    # "contract.plan": 1,
                    # "contract.monthly_xaf": 1,
                }
                },
            ],
        }
    },
]

result = list(col.aggregate(pipeline))[0]
print(f'Regions x types : {len(result["by_region_type"])} groupes')

print("\n=== CA par région et type client ===")
for row in result["by_region_type"]:
    print(row)

print("\n=== CA par plan tarifaire ===")
for row in result["by_plan"]:
    print(row)

print("\n=== Top 10 distributeurs ===")
for row in result["top_distributors"]:
    print(row)

print("\n=== Top 10 contrats les plus élevés ===")
for row in result["outliers_ca"]:
    print(row)
