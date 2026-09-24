from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base
class ClientBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

# Crear Cliente
class ClientCreate(ClientBase):
    pass

# Actualizar Cliente
class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

# Respuesta para listados desplegables (Dropdowns)
class ClientBasicResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

# Respuesta para la Tabla y Detalles
class ClientResponse(ClientBase):
    id_client: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Respuesta Paginada
class PaginatedClientResponse(BaseModel):
    items: List[ClientResponse]
    total: int