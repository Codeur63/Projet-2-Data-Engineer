from datetime import datetime
from solarmboa.database import get_db


def bootstrap():
    db = get_db()
    collection = db["installations"]
    print("Base de données :", db)

    sample_documents = {
        "installation_id": 1,
        "client_name": "Centre de Yaoundé",
        "client_type": "health_center",
        "status": "active",
        "location": {
            "city": "Yaoundé",
            "region": "Centre",
            "gps": {"type": "Point", "coordinates": [11.5021, 3.8480]},
        },
        "contract": {"plan": "Premium", "monthly_xaf": 35000},
        "created_at": datetime.utcnow(),
    }

    result = collection.insert_one(sample_documents)

    print(f"Document inséré avec Id :{result.inserted_id} ")


if __name__ == "__main__":
    bootstrap()
