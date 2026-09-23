from uuid import UUID
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from models.sensor import Sensor
from models.device import Device
from schemas.sensor_schema import SensorCreate, SensorUpdate
from models.sensor import Sensor, SensorType

# MAPPER AUXILIAR DE RESPUESTA
def map_sensor_to_response(sensor: Sensor) -> dict:
    return {
        "id_sensor": sensor.id_sensor,
        "id_device": sensor.id_device,
        "device_code": sensor.device.code if sensor.device else "N/A",
        "id_sensor_type": sensor.id_sensor_type,
        "sensor_type_name": sensor.sensor_type.name if sensor.sensor_type else "Desconocido",
        "code": sensor.code,
        "location": sensor.location,
        "is_active": sensor.is_active,
    }

# LISTAR SENSORES (PAGINACIÓN A 5 REGISTROS POR PÁGINA)
async def list_sensors(
    db: AsyncSession,
    device_id: Optional[UUID] = None,
    limit: int = 5,  # 👈 Tamaño estricto de a 5 filas por página
    offset: int = 0
):
    query = (
        select(Sensor)
        .options(
            selectinload(Sensor.device),
            selectinload(Sensor.sensor_type)
        )
    )

    if device_id:
        query = query.where(Sensor.id_device == device_id)

    query = query.order_by(Sensor.is_active.desc(), Sensor.code.asc())

    # Total para la paginación del frontend
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    sensors = result.scalars().all()

    return {
        "items": [map_sensor_to_response(s) for s in sensors],
        "total": total
    }

# CREAR SENSOR
async def create_sensor(db: AsyncSession, payload: SensorCreate):
    # Validar código único
    existing = await db.execute(select(Sensor).where(Sensor.code == payload.code.strip().upper()))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un sensor registrado con el código '{payload.code}'"
        )

    sensor = Sensor(
        id_device=payload.id_device,
        id_sensor_type=payload.id_sensor_type,
        code=payload.code.strip().upper(),
        location=payload.location.strip() if payload.location else None,
        is_active=True
    )
    db.add(sensor)
    await db.commit()

    # Recargar con relaciones sin usar db.refresh(sensor) para prevenir errores asíncronos
    updated_result = await db.execute(
        select(Sensor)
        .where(Sensor.id_sensor == sensor.id_sensor)
        .options(selectinload(Sensor.device), selectinload(Sensor.sensor_type))
    )
    return map_sensor_to_response(updated_result.scalars().first())

# ACTUALIZAR SENSOR
async def update_sensor(db: AsyncSession, sensor_id: UUID, payload: SensorUpdate):
    result = await db.execute(
        select(Sensor)
        .where(Sensor.id_sensor == sensor_id)
        .options(selectinload(Sensor.device), selectinload(Sensor.sensor_type))
    )
    sensor = result.scalars().first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(sensor, key, value)

    await db.commit()

    # Volver a consultar la entidad limpia
    updated_result = await db.execute(
        select(Sensor)
        .where(Sensor.id_sensor == sensor_id)
        .options(selectinload(Sensor.device), selectinload(Sensor.sensor_type))
    )
    return map_sensor_to_response(updated_result.scalars().first())

# TOGGLE STATUS (ACTIVAR / DESACTIVAR)
async def toggle_sensor_status(db: AsyncSession, sensor_id: UUID):
    result = await db.execute(
        select(Sensor)
        .where(Sensor.id_sensor == sensor_id)
        .options(selectinload(Sensor.device), selectinload(Sensor.sensor_type))
    )
    sensor = result.scalars().first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

    sensor.is_active = not sensor.is_active
    await db.commit()

    updated_result = await db.execute(
        select(Sensor)
        .where(Sensor.id_sensor == sensor_id)
        .options(selectinload(Sensor.device), selectinload(Sensor.sensor_type))
    )
    return map_sensor_to_response(updated_result.scalars().first())