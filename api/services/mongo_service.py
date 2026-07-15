from typing import Optional, Dict, Any

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from api.core.config import settings


class MongoService:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_database]
        self.installations: Collection = self.db["installations"]

        self.installations.create_index(
            [("installation_id", ASCENDING)],
            unique=True,
            name="idx_installation_id_unique",
        )

    def create_installation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.installations.insert_one(payload)
            created = True
        except DuplicateKeyError:
            created = False
            
        installation = self.get_installation(payload["installation_id"])
        
        return {
            "created": created,
            "installation": installation,
        }    

        # existing = self.installations.find_one(
        #     {"installation_id": payload["installation_id"]},
        #     {"_id": 0},
        # )

        # if existing:
        #     return {
        #         "created": False,
        #         "installation": existing,
        #     }

        # self.installations.insert_one(payload)

        # created = self.installations.find_one(
        #     {"installation_id": payload["installation_id"]},
        #     {"_id": 0},
        # )

        # return {
        #     "created": True,
        #     "installation": created,
        # }

    def get_installation(self, installation_id: int) -> Optional[Dict[str, Any]]:
        return self.installations.find_one(
            {"installation_id": installation_id},
            {"_id": 0},
        )

    def update_status(self, installation_id: int, status: str) -> Optional[Dict[str, Any]]:
        result = self.installations.find_one_and_update(
            {"installation_id": installation_id},
            {"$set": {"status": status}},
            projection={"_id": 0},
            return_document=True,
        )

        return result
    
    def delete_installation(self, installation_id : int):
        
        delInstallation = False 
        try:
            self.installations.remove(
                {"installation_id":installation_id} 
                ) 
            delInstallation = True
        except:
            return("Non trouvé")    

        return {
            "installation": installation_id,
            "delete": delInstallation
        }
        
        
    def add_maintenance(
        self,
        installation_id: int,
        maintenance_payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        installation = self.get_installation(installation_id)

        if installation is None:
            return None

        self.installations.update_one(
            {"installation_id": installation_id},
            {
                "$push": {
                    "maintenance_history": maintenance_payload
                }
            },
        )

        return self.get_installation(installation_id)    

mongo_service = MongoService()