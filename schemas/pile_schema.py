from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class PileCreate(BaseModel):
    id_greenhouse: UUID
    code: str = Field(..., min_length=2, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    process_start_date: datetime
    estimated_end_date: Optional[datetime] = None
    base_material: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)

class PileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    process_start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=30)
    base_material: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)
class PileListItemResponse(BaseModel):
    id_pile: UUID
    id_greenhouse: UUID
    code: str
    name: Optional[str] = None
    process_start_date: datetime
    estimated_end_date: Optional[datetime] = None
    status: str
    created_at: datetime
    assigned_device_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class PileDetailResponse(BaseModel):
    id_pile: UUID
    id_greenhouse: UUID
    code: str
    name: Optional[str] = None
    process_start_date: datetime
    estimated_end_date: Optional[datetime] = None
    status: str
    base_material: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    assigned_device_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedPileResponse(BaseModel):
    items: List[PileListItemResponse]
    total: int