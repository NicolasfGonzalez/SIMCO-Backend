from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

#  Usados por CRUD Usuarios
class GreenhouseBase(BaseModel):
    name: str

class GreenhouseBasicResponse(BaseModel):
    id_greenhouse: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class GreenhouseResponse(BaseModel):
    id_greenhouse: UUID
    name: str
    id_client: UUID

    model_config = ConfigDict(from_attributes=True)

class GreenhouseListResponse(BaseModel):
    items: List[GreenhouseResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Para CRUD propio de Invernaderos
class GreenhouseCreate(BaseModel):
    id_client: UUID
    name: str = Field(..., min_length=3, max_length=100)
    location: str = Field(..., min_length=3, max_length=200)
    latitude: float
    longitude: float

class GreenhouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    location: Optional[str] = Field(None, min_length=3, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None

# Respuesta para la tabla principal (DataGrid)
class GreenhouseCrudListResponse(BaseModel):
    id_greenhouse: UUID
    name: str
    location: str
    is_active: bool
    status: str
    responsables: List[str] = [] 

    model_config = ConfigDict(from_attributes=True)

class PaginatedGreenhouseResponse(BaseModel):
    items: List[GreenhouseCrudListResponse]
    total: int

# Respuesta para el modal de Detalles / Edición
class GreenhouseDetailResponse(BaseModel):
    id_greenhouse: UUID
    id_client: UUID
    name: str
    location: str
    latitude: float
    longitude: float
    is_active: bool
    status: str
    created_at: datetime
    responsables: List[str] = []

    model_config = ConfigDict(from_attributes=True)