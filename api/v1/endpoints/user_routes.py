from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user_service import create_user, update_user
from schemas.user import UserListResponse
from services.user_service import list_users
from services.user_service import toggle_user_status


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

# Endpoints de Usuario Listar
@router.get("/", response_model=list[UserListResponse])
async def list_users_endpoint(
    client_id: UUID | None = None,
    limit: int = 10,
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