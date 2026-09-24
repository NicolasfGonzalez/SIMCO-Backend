from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# CATÁLOGO DE TIPOS DE SENSOR (sensor_type)
# ============================================================
class SensorTypeResponse(BaseModel):
    id_sensor_type: int
    name: str
    unit: str

    model_config = ConfigDict(from_attributes=True)

# ============================================================
# SENSORES
# ============================================================
class SensorCreate(BaseModel):
    id_sensor_type: int
    code: str = Field(..., min_length=2, max_length=50) # Ej: SENS-TEMP-01
    location: Optional[str] = Field(None, max_length=100) # Ej: Zona Superior

class SensorResponse(BaseModel):
    id_sensor: UUID
    id_device: UUID
    id_sensor_type: int
    code: str
    location: Optional[str] = None
    is_active: bool
    sensor_type: Optional[SensorTypeResponse] = None

    model_config = ConfigDict(from_attributes=True)

# ============================================================
# DISPOSITIVOS IOT
# ============================================================
class DeviceCreate(BaseModel):
    id_greenhouse: UUID
    code: str = Field(..., min_length=3, max_length=50) # Ej: ESP32-NODE-01
    description: Optional[str] = Field(None, max_length=200)
    sensors: Optional[List[SensorCreate]] = []

class DeviceUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    sensors: Optional[List[SensorCreate]] = None

class DeviceListResponse(BaseModel):
    id_device: UUID
    id_greenhouse: UUID
    id_pile: Optional[UUID] = None
    code: str
    description: Optional[str] = None
    assigned_pile_code: Optional[str] = None
    sensors_count: int = 0
    is_active: bool
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedDeviceResponse(BaseModel):
    items: List[DeviceListResponse]
    total: int

class DeviceDetailResponse(DeviceListResponse):
    sensors: List[SensorResponse] = []

    model_config = ConfigDict(from_attributes=True)