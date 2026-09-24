from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.greenhouse_schema import (
    GreenhouseCreate,
    GreenhouseUpdate,
    PaginatedGreenhouseResponse,
    GreenhouseDetailResponse,
    GreenhouseBasicResponse,
    AssignUsersPayload
)
from services.greenhouse_service import (
    create_greenhouse,
    list_greenhouses,
    get_greenhouse_by_id,
    update_greenhouse,
    toggle_greenhouse_status,
    get_greenhouses_by_client,
    assign_users_to_greenhouse
)   

router = APIRouter(prefix="/greenhouses", tags=["Greenhouses"])

# Endpoint para obtener invernaderos por cliente
@router.get("/by-client/{client_id}", response_model=List[GreenhouseBasicResponse])
async def get_greenhouses_by_client_endpoint(
    client_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    return await get_greenhouses_by_client(db, client_id)

# Endpoint para listar invernaderos con paginación y filtrado por cliente   
@router.get("/", response_model=PaginatedGreenhouseResponse)
async def list_greenhouses_endpoint(
    client_id: Optional[UUID] = Query(None),
    limit: int = Query(4, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await list_greenhouses(db, client_id, limit, offset)

# Endpoint para crear un nuevo invernadero
@router.post("/", response_model=GreenhouseDetailResponse)
async def create_greenhouse_endpoint(
    gh_in: GreenhouseCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await create_greenhouse(db, gh_in)

# Endpoint para obtener un invernadero por su ID
@router.get("/{gh_id}", response_model=GreenhouseDetailResponse)
async def get_greenhouse_endpoint(
    gh_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    return await get_greenhouse_by_id(db, gh_id)

# Endpoint para actualizar un invernadero
@router.put("/{gh_id}", response_model=GreenhouseDetailResponse)
async def update_greenhouse_endpoint(
    gh_id: UUID, 
    gh_in: GreenhouseUpdate, 
    db: AsyncSession = Depends(get_db)
):
    return await update_greenhouse(db, gh_id, gh_in)

# Endpoint para cambiar el estado de un invernadero (activo/inactivo)
@router.patch("/{gh_id}/toggle-status", response_model=GreenhouseDetailResponse)
async def toggle_greenhouse_status_endpoint(
    gh_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    return await toggle_greenhouse_status(db, gh_id)

# Endpoint para asignar usuarios a un invernadero
@router.put("/{gh_id}/users", response_model=GreenhouseDetailResponse)
async def update_greenhouse_users_endpoint(
    gh_id: UUID,
    payload: AssignUsersPayload,
    db: AsyncSession = Depends(get_db)
):
    return await assign_users_to_greenhouse(db, gh_id, payload.user_ids)