from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

REGION = Literal[ "Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral", "Nord-Ouest", "Ouest" ]
ALERT = Literal["AUCUNE","ERR","FAULT_01","FAULT_02","LOW_BAT","NO_SIG","OVERCURRENT","OVR_V","TAMPER"
]

class TelemetryIn(BaseModel):
    sensor_id: str
    installation_id: int
    timestamp: datetime
    solar_output_w: float = Field(ge=0)
    battery_level_pct: float = Field(ge=0, le=100)
    consumption_w: float = Field(ge=0)
    alert_code: ALERT
    region: REGION


class TelemetryBatchIn(BaseModel):
    items: List[TelemetryIn]