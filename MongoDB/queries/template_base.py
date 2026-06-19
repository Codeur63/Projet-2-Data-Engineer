"""Template a copier pour chaque requete MQL."""

import sys
from pathlib import Path
from src.solarmboa.database import get_db

sys.path.insert(0, str(Path(__file__).parent.parent))

db = get_db()
col = db["installations"]


# -- Exemple de requete : compter les installations par region
pipeline = [
    {"$group": {"_id": "$location.region", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]

resultats = list(col.aggregate(pipeline))
print("Installations par region :")
for r in resultats:
    print(f'- {r["_id"]}: {r["count"]:,}')


if __name__ == "__main__":
    pass
