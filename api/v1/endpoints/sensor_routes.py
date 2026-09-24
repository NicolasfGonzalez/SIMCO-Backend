from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.sensor_schema import (
    SensorCreate,
    SensorUpdate,
    SensorResponse,
    PaginatedSensorResponse
)
from services.sensor_service import (
    create_sensor,
    list_sensors,
    update_sensor,
    toggle_sensor_status
)

router = APIRouter(prefix="/sensors", tags=["Sensores IoT"])

@router.get("/", response_model=PaginatedSensorResponse)
async def list_sensors_endpoint(
    device_id: Optional[UUID] = Query(None, description="Filtro opcional por Nodo Dispositivo"),
    limit: int = Query(5, ge=1, le=100, description="Cantidad de registros por página (defecto: 5)"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(get_db)
):
    return await list_sensors(db=db, device_id=device_id, limit=limit, offset=offset)

@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor_endpoint(
    payload: SensorCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_sensor(db, payload)

@router.put("/{sensor_id}", response_model=SensorResponse)
async def update_sensor_endpoint(
    sensor_id: UUID,
    payload: SensorUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_sensor(db, sensor_id, payload)

@router.patch("/{sensor_id}/toggle-status", response_model=SensorResponse)
async def toggle_sensor_status_endpoint(
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await toggle_sensor_status(db, sensor_id)