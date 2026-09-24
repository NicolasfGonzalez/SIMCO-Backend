from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class SensorCreate(BaseModel):
    id_device: UUID
    id_sensor_type: int
    code: str = Field(..., min_length=2, max_length=50)
    location: Optional[str] = Field(None, max_length=100)

class SensorUpdate(BaseModel):
    location: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class SensorResponse(BaseModel):
    id_sensor: UUID
    id_device: UUID
    device_code: str
    id_sensor_type: int
    sensor_type_name: str
    code: str
    location: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class PaginatedSensorResponse(BaseModel):
    items: List[SensorResponse]
    total: int