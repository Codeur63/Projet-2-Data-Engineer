from typing import Optional, Literal
from pydantic import BaseModel, Field


ClientType = Literal[ "residential", "sme", "health_center", "school" ]
TariffPlan = Literal[ "Basic", "Standard", "Premium", "Custom" ]
Status = Literal[ "active", "suspended", "maintenance", "churned" ]
Region = Literal[ "Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral", "Nord-Ouest", "Ouest" ]
Distributor = Literal[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]


class InstallationCreate(BaseModel):
    installation_id: int
    client_name: str
    client_type: ClientType
    distributor_id: Distributor
    status: Status = "active"
    location: dict = {
        "city": str,
        "region": Region,
        "gps" : {
            "type":"Point",
            "coordinates": [
                "gps_lat", 
                "gps_lon"
            ]
        }
    },
    contract : dict = {
        "plan": TariffPlan,
        "monthly_xaf" : float 
    },
    solar_system: dict =  {
      "installation_date": str,
      "panel_capacity_wp": Optional[float],
      "battery_capacity_wh": Optional[float],
      "num_appliances": int
    }
    
    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return None
        data["_id"] = str(data["_id"])
        return cls(**data)

class InstallationStatusUpdate(BaseModel):
    status: Status

