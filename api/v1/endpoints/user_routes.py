from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from pydantic import BaseModel

from typing import List, Optional

from core.database import get_db

from schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserDetailResponse,
)

from services.user_service import (
    create_user,
    update_user,
    list_users,
    toggle_user_status,
    get_user_by_id,
)

router = APIRouter(prefix="/users",tags=["Users"])

# CREAR USUARIO
@router.post(
    "/",
    response_model=UserResponse
)
async def create_user_endpoint(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user)

# ACTUALIZAR USUARIO
@router.put(
    "/{user_id}",
    response_model=UserDetailResponse
)
async def update_user_endpoint(
    user_id: UUID,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_user(
        db,
        user_id,
        user
    )

class PaginatedUsersResponse(BaseModel):
    items: List[UserListResponse]
    total: int

# LISTAR USUARIOS
@router.get(
    "/",
    response_model=PaginatedUsersResponse
)
async def list_users_endpoint(
    client_id: Optional[UUID] = None,
    search: Optional[str] = None,
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await list_users(
        db=db,
        client_id=client_id,
        search=search,
        limit=limit,
        offset=offset
    )

# ACTIVAR / DESACTIVAR USUARIO
@router.patch(
    "/{user_id}/toggle-status",
    response_model=UserResponse
)
async def toggle_user_status_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await toggle_user_status(
        db,
        user_id
    )

# OBTENER USUARIO POR ID
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