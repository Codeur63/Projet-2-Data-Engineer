"""
Applique une validation JSON Schema sur la collection installations.
A executer apres l'import (une seule fois).
"""
from solarmboa.database import get_db


def create_validation():
    db = get_db()
    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "installation_id",
                "client_type",
                "status",
                "distributor_id",
                "location",
                "contract",
            ],
            "properties": {
                "installation_id": {"bsonType": ["int", "long"], "minimum": 1},
                "client_type": {
                    "bsonType": "string",
                    "enum": ["residential", "sme", "health_center", "school"],
                },
                "status": {
                    "bsonType": "string",
                    "enum": [
                        "active",
                        "suspended",
                        "maintenance",
                        "churned",
                        "pending",
                        "unknown",
                    ],
                },
                "distributor_id": {"bsonType": ["int", "long"]},
                "location": {
                    "bsonType": "object",
                    "required": ["city", "region"],
                    "properties": {
                        "city": {"bsonType": "string"},
                        "region": {
                            "bsonType": "string",
                            "enum": [
                                "Littoral",
                                "Centre",
                                "Ouest",
                                "Nord-Ouest",
                                "Adamaoua",
                                "Est",
                                "Extreme-Nord",
                                "Nord",
                                "Sud",
                                "Sud-Ouest",
                            ],
                        },
                        "gps": {
                            "bsonType": "object",
                            "required": ["type", "coordinates"],
                            "properties": {
                                "type": {"bsonType": "string", "enum": ["Point"]},
                                "coordinates": {
                                    "bsonType": "array",
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "items": {              
                                        "bsonType": "double"      
                                    }
                                },
                            },
                        },
                    },
                },
                "contract": {
                    "bsonType": "object",
                    "required": ["plan", "monthly_xaf"],
                    "properties": {
                        "plan": {
                            "bsonType": "string",
                            "enum": ["Basic", "Standard", "Premium", "Custom"],
                        },
                        "monthly_xaf": {"bsonType": ["int", "double"], "minimum": 0},
                    },
                },
            },
        }
    }

    
    db.command(
        "collMod",
        "installations",
        validator=schema,
        validationAction="error",
        validationLevel="moderate",
    )
    
    
    print("Schema validation applique sur la collection installations.")


if __name__ == "__main__":
    create_validation()
