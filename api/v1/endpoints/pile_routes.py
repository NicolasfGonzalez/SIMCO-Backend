from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from core.database import get_db
from core.mongo import get_mongo_db
from schemas.pile_schema import (
    PileCreate,
    PileUpdate,
    PileDetailResponse,
    PaginatedPileResponse,
)
from services.pile_service import (
    create_pile,
    list_piles,
    get_pile_by_id,
    update_pile,
    assign_device_to_pile,
)

router = APIRouter(prefix="/piles", tags=["Pilas de Compostaje"])


class AssignDevicePayload(BaseModel):
    device_code: Optional[str] = None

# Endpoints para la gestión de pilas de compostaje
@router.post("/", response_model=PileDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_pile_endpoint(
    payload: PileCreate,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    return await create_pile(db, mongo_db, payload)

# Endpoint para listar pilas de compostaje con paginación
@router.get("/", response_model=PaginatedPileResponse)
async def list_piles_endpoint(
    greenhouse_id: Optional[UUID] = Query(None, description="Filtrar por ID de invernadero"),
    limit: int = Query(4, ge=1, le=100, description="Registros por página (Por defecto: 4)"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    return await list_piles(
        db=db,
        mongo_db=mongo_db,
        greenhouse_id=greenhouse_id,
        limit=limit,
        offset=offset,
    )

# Endpoint para obtener detalles de una pila específica por su ID
@router.get("/{pile_id}", response_model=PileDetailResponse)
async def get_pile_endpoint(
    pile_id: UUID,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    return await get_pile_by_id(db, mongo_db, pile_id)

# Endpoint para actualizar los detalles de una pila específica
@router.put("/{pile_id}", response_model=PileDetailResponse)
async def update_pile_endpoint(
    pile_id: UUID,
    payload: PileUpdate,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    return await update_pile(db, mongo_db, pile_id, payload)

# Endpoint para asignar un dispositivo a una pila específica
@router.patch("/{pile_id}/assign-device", response_model=PileDetailResponse)
async def assign_device_endpoint(
    pile_id: UUID,
    payload: AssignDevicePayload,
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    return await assign_device_to_pile(db, mongo_db, pile_id, payload.device_code)


# Endpoint para obtener telemetría de una pila específica desde MongoDB
@router.get("/{pile_code}/telemetry")
async def get_pile_telemetry_endpoint(
    pile_code: str,
    limit: int = Query(5, ge=1, le=500),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    if mongo_db is None:
        return []

    # Buscar telemetría en MongoDB filtrando por pile_code
    cursor = (
        mongo_db["telemetry"]
        .find({"metadata.pile_code": pile_code.upper()}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )

    telemetry_data = await cursor.to_list(length=limit)
    return telemetry_data[::-1]  