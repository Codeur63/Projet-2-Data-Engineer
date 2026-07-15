from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


MaintenanceType = Literal["preventive", "corrective", "inspection"]
MaintenanceStatus = Literal["planned", "in_progress", "completed", "cancelled"]


class MaintenanceCreate(BaseModel):
    maintenance_id: str
    maintenance_type: MaintenanceType
    technician_id: str
    intervention_date: date
    issue: str = Field(min_length=3)
    resolution: Optional[str] = None
    cost_xaf: float = Field(ge=0)
    status: MaintenanceStatus = "completed"