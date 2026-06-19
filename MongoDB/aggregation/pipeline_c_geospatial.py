"""
Utilise l'index 2dsphere pour trouver les installations proches
d'un technicien donne.
"""

from solarmboa.database import get_db

col = get_db()["installations"]
# Coordonnees du technicien TECH-0042 (Douala)

tech_lon, tech_lat = 9.7180, 4.0605
# $geoNear DOIT etre le premier stage du pipeline
# Index 2dsphere requis sur location.gps

pipeline = [
    {
        "$geoNear": {
            "near": {"type": "Point", "coordinates": [tech_lon, tech_lat]},
            "distanceField": "distance_m",
            "maxDistance": 50000,
            # 50 km en metres
            "spherical": True,
            "query": {"status": "maintenance"},
        }
    },
    {
        "$project": {
            "installation_id": 1,
            "client_name": 1,
            "location.city": 1,
            "location.region": 1,
            "status": 1,
            "distance_km": {"$round": [{"$divide": ["$distance_m", 1000]}, 2]},
        }
    },
    {"$sort": {"distance_km": 1}},
    {"$limit": 10},
]

result = list(col.aggregate(pipeline))
print(f"Installations en maintenance dans 50 km : {len(result)}")

for r in result:
    print(
        f' {r["installation_id"]:>5} | {r["location"]["city"]:15} | {r["distance_km"]:.2f} km'
    )
