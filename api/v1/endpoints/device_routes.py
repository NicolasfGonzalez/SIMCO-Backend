from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.device_schema import (
    DeviceCreate,
    DeviceUpdate,
    DeviceDetailResponse,
    PaginatedDeviceResponse,
    SensorTypeResponse
)
from services.device_service import (
    create_device,
    list_devices,
    get_device_by_id,
    toggle_device_status,
    update_device,
    get_sensor_types
)

router = APIRouter(prefix="/devices", tags=["Dispositivos IoT"])

#  CATÁLOGO TIPOS DE SENSORES (Ubicación estática previa)
@router.get("/sensor-types", response_model=List[SensorTypeResponse])
async def get_sensor_types_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_sensor_types(db)

#  LISTAR DISPOSITIVOS PAGINADOS
@router.get("/", response_model=PaginatedDeviceResponse)
async def list_devices_endpoint(
    greenhouse_id: Optional[UUID] = Query(None, description="Filtro opcional por Invernadero"),
    limit: int = Query(3, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await list_devices(db, greenhouse_id=greenhouse_id, limit=limit, offset=offset)

#  CREAR DISPOSITIVO CON SENSORES
@router.post("/", response_model=DeviceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_device_endpoint(
    payload: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_device(db, payload)

#  OBTENER DETALLE POR ID (Ruta Parametrizada)
@router.get("/{device_id}", response_model=DeviceDetailResponse)
async def get_device_endpoint(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await get_device_by_id(db, device_id)

#  CAMBIAR ESTADO (ACTIVAR / DESACTIVAR)
@router.patch("/{device_id}/toggle-status", response_model=DeviceDetailResponse)
async def toggle_status_endpoint(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await toggle_device_status(db, device_id)

#  ACTUALIZAR DISPOSITIVO
@router.put("/{device_id}", response_model=DeviceDetailResponse)
async def update_device_endpoint(
    device_id: UUID,
    payload: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_device(db, device_id, payload)