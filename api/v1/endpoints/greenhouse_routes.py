from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from schemas.greenhouse_schema import (
    GreenhouseCreate,
    GreenhouseUpdate,
    PaginatedGreenhouseResponse,
    GreenhouseDetailResponse,
    GreenhouseListResponse,
    GreenhouseBasicResponse,
)

from services.greenhouse_service import (
    create_greenhouse,
    list_greenhouses,
    get_greenhouse_by_id,
    update_greenhouse,
    toggle_greenhouse_status,
    get_greenhouses_by_client,
)


router = APIRouter(prefix="/greenhouses",tags=["Greenhouses"])

# CRUD - LISTAR INVERNADEROS
@router.get(
    "/",
    response_model=PaginatedGreenhouseResponse,
    summary="Listar invernaderos",
    description="Obtiene los invernaderos registrados con paginación y filtro opcional por cliente."
)
async def list_greenhouses_endpoint(
    client_id: Optional[UUID] = Query(
        default=None,
        description="UUID del cliente por el cual se desea filtrar."
    ),
    limit: int = Query(
        default=50,
        ge=1,
        description="Cantidad máxima de registros que se desean obtener."
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Cantidad de registros que se desean omitir."
    ),
    db: AsyncSession = Depends(get_db),
):
    return await list_greenhouses(
        db,
        client_id,
        limit,
        offset
    )


# CRUD - CREAR INVERNADERO
@router.post(
    "/",
    response_model=GreenhouseDetailResponse,
    summary="Crear invernadero",
    description="Registra un nuevo invernadero."
)
async def create_greenhouse_endpoint(
    gh_in: GreenhouseCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_greenhouse(
        db,
        gh_in
    )


# CRUD - OBTENER INVERNADERO POR ID
@router.get(
    "/{gh_id}",
    response_model=GreenhouseDetailResponse,
    summary="Obtener invernadero por ID",
    description="Obtiene la información detallada de un invernadero mediante su UUID."
)
async def get_greenhouse_endpoint(
    gh_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    return await get_greenhouse_by_id(
        db,
        gh_id
    )


# CRUD - ACTUALIZAR INVERNADERO
@router.put(
    "/{gh_id}",
    response_model=GreenhouseDetailResponse,
    summary="Actualizar invernadero",
    description="Actualiza la información de un invernadero existente."
)
async def update_greenhouse_endpoint(
    gh_id: UUID,
    gh_in: GreenhouseUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_greenhouse(
        db,
        gh_id,
        gh_in
    )


# CRUD - ACTIVAR / DESACTIVAR
@router.patch(
    "/{gh_id}/toggle-status",
    response_model=GreenhouseDetailResponse,
    summary="Cambiar estado del invernadero",
    description="Activa o desactiva un invernadero."
)
async def toggle_greenhouse_status_endpoint(
    gh_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await toggle_greenhouse_status(
        db,
        gh_id
    )


# CONSULTA - INVERNADEROS POR CLIENTE

@router.get(
    "/by-client/{client_id}",
    response_model=list[GreenhouseBasicResponse],
    summary="Obtener invernaderos por cliente",
    description="Obtiene únicamente los invernaderos asociados a un cliente específico."
)
async def get_greenhouses_by_client_endpoint(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_greenhouses_by_client(
        db,
        client_id
    )