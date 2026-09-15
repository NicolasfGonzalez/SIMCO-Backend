from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from typing import List, Optional
from uuid import UUID

from core.database import get_db

from schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientBasicResponse,
    PaginatedClientResponse
)
from services.client_service import (
    list_clients_basic,
    create_client,
    list_clients,
    get_client_by_id,
    update_client,
    get_all_clients_basic
)


# Endpoints para listar todos los clientes
router = APIRouter(prefix="/clients", tags=["Clients"])
@router.get("/basic", response_model=List[ClientBasicResponse])
async def get_clients_basic(db: AsyncSession = Depends(get_db)):
    return await list_clients_basic(db)

# 1. Selector/Dropdown de clientes (Utilizado en otros módulos)
@router.get("/selector", response_model=List[ClientBasicResponse])
async def get_clients_selector_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_all_clients_basic(db)

# 2. Listar Clientes con Paginación
@router.get("/", response_model=PaginatedClientResponse)
async def list_clients_endpoint(
    search: Optional[str] = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await list_clients(db, search, limit, offset)

# 3. Crear Cliente
@router.post("/", response_model=ClientResponse)
async def create_client_endpoint(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_client(db, client_in)

# 4. Obtener un Cliente por ID
@router.get("/{client_id}", response_model=ClientResponse)
async def get_client_endpoint(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await get_client_by_id(db, client_id)

# 5. Actualizar Cliente
@router.put("/{client_id}", response_model=ClientResponse)
async def update_client_endpoint(
    client_id: UUID,
    client_in: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_client(db, client_id, client_in)