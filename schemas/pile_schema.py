from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# 1. ESQUEMA DE CREACIÓN
# ============================================================
class PileCreate(BaseModel):
    id_greenhouse: UUID
    code: str = Field(..., min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    process_start_date: datetime
    location: Optional[str] = None
    estimated_end_date: Optional[datetime] = None
    base_material: Optional[str] = None
    notes: Optional[str] = None

# ============================================================
# 2. ESQUEMA DE ACTUALIZACIÓN (Edición Parcial)
# ============================================================
class PileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    process_start_date: Optional[datetime] = None
    location: Optional[str] = None
    estimated_end_date: Optional[datetime] = None
    status: Optional[str] = None
    base_material: Optional[str] = None
    notes: Optional[str] = None

UpdatePilePayload = PileUpdate

# ============================================================
# 3. ESQUEMA DE RESPUESTA PARA LISTA (Paginación Tabla Frontend)
# ============================================================
class PileListResponse(BaseModel):
    id_pile: UUID
    id_greenhouse: UUID
    code: str
    name: Optional[str] = None
    process_start_date: datetime
    created_at: datetime
    assigned_device_code: Optional[str] = None
    status: str = "Activa"

    model_config = ConfigDict(from_attributes=True)

class PaginatedPileResponse(BaseModel):
    items: List[PileListResponse]
    total: int

# ============================================================
# 4. ESQUEMA DE DETALLE COMPLETO (PostgreSQL + MongoDB Atlas)
# ============================================================
class PileDetailResponse(BaseModel):
    id_pile: UUID
    id_greenhouse: UUID
    code: str
    name: Optional[str] = None
    process_start_date: datetime
    created_at: datetime
    assigned_device_code: Optional[str] = None
    location: Optional[str] = None
    estimated_end_date: Optional[datetime] = None
    status: str = "Activa"
    base_material: Optional[str] = None
    notes: Optional[str] = None
    latest_readings: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)