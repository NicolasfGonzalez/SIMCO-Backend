from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from uuid import UUID

from core.database import get_db
from core.mongo import get_mongo_db
from schemas.pile_schema import (
    PileCreate,
    PileUpdate,
    PileDetailResponse,
    PaginatedPileResponse
)
from services.pile_service import (
    create_pile,
    list_piles,
    get_pile_by_id,
    update_pile,
    assign_device_to_pile
)

router = APIRouter(prefix="/piles", tags=["Pilas de Compostaje"])

# 1. Crear Pila
@router.post("/", response_model=PileDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_pile_endpoint(
    payload: PileCreate,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    return await create_pile(db, mongo_db, payload)

# 2. Listar Pilas Paginadas
@router.get("/", response_model=PaginatedPileResponse)
async def list_piles_endpoint(
    greenhouse_id: Optional[UUID] = Query(None, description="Filtro opcional por Invernadero"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad de registros por página"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    return await list_piles(
        db=db, 
        mongo_db=mongo_db, 
        greenhouse_id=greenhouse_id, 
        limit=limit, 
        offset=offset
    )
# 3. Obtener Detalle Completo
@router.get("/{pile_id}", response_model=PileDetailResponse)
async def get_pile_endpoint(
    pile_id: UUID,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    return await get_pile_by_id(db, mongo_db, pile_id)

# 4. Actualizar Pila
@router.put("/{pile_id}", response_model=PileDetailResponse)
async def update_pile_endpoint(
    pile_id: UUID,
    payload: PileUpdate,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    return await update_pile(db, mongo_db, pile_id, payload)

# 5. Asignar Nodo IoT
@router.patch("/{pile_id}/assign-device/{device_code}")
async def assign_device_endpoint(
    pile_id: UUID,
    device_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await assign_device_to_pile(db, pile_id, device_code)