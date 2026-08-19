from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel
from typing import List

from core.database import get_db
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user_service import create_user, update_user
from schemas.user import UserListResponse
from services.user_service import list_users
from services.user_service import toggle_user_status
from services.user_service import get_user_by_id
from schemas.user import UserDetailResponse

router = APIRouter(prefix="/users", tags=["Users"])

# Endpoints de Usuario Crear
@router.post("/", response_model=UserResponse)
async def create_user_endpoint(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user)

# Endpoints de Usuario Actualizar
@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: UUID,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_user(db, user_id, user)
class PaginatedUsersResponse(BaseModel):
    items: List[UserListResponse]
    total: int

# Endpoints de Usuario Listar
@router.get("/", response_model=PaginatedUsersResponse)
async def list_users_endpoint(
    client_id: UUID | None = None,
    limit: int = 5,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await list_users(db, client_id, limit, offset)

# Endpoints de Usuario Desactivar / Activar
@router.patch("/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await toggle_user_status(db, user_id)

# En
@router.get(
    "/{user_id}",
    response_model=UserDetailResponse
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):

    return await get_user_by_id(
        db,
        user_id
    )