import re

from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ConfigDict,
)


# CREAR USUARIO
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    id_role: int

    # Invernaderos que se asignarán al usuario
    greenhouse_ids: List[UUID] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "El nombre debe tener al menos 3 caracteres"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Mínimo 8 caracteres")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Debe tener una mayúscula")

        if not re.search(r"[a-z]", value):
            raise ValueError("Debe tener una minúscula")

        if not re.search(r"[0-9]", value):
            raise ValueError("Debe tener un número")

        return value


# RESPUESTA GENERAL DE USUARIO
class UserResponse(BaseModel):
    id_user: UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    role: str
    client: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ACTUALIZAR USUARIO
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    id_role: Optional[int] = None
    id_client: Optional[UUID] = None

    greenhouse_ids: Optional[List[UUID]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value and len(value.strip()) < 3:
            raise ValueError(
                "El nombre debe tener al menos 3 caracteres"
            )

        return value


# LISTAR USUARIO
class UserListResponse(BaseModel):
    id_user: UUID
    name: str
    email: EmailStr
    role: str
    status: str


# DETALLE COMPLETO DEL USUARIO
class UserDetailResponse(BaseModel):
    id_user: UUID
    name: str
    email: EmailStr
    id_role: int
    role: str
    is_active: bool
    status: str

    client_id: Optional[UUID] = None

    greenhouse_ids: List[str] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


# LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    password: str

UpdateUserPayload = UserUpdate