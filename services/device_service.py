from uuid import UUID
from typing import Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from models.device import Device
from models.sensor import Sensor, SensorType
from schemas.device_schema import DeviceCreate, DeviceUpdate

# ============================================================
# 1. LISTAR DISPOSITIVOS PAGINADOS
# ============================================================

# ============================================================
# 2. CREAR DISPOSITIVO CON SENSORES INICIALES
# ============================================================
async def create_device(db: AsyncSession, payload: DeviceCreate):
    existing = await db.execute(select(Device).where(Device.code == payload.code.strip().upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El código de dispositivo '{payload.code}' ya existe"
        )

    new_device = Device(
        id_greenhouse=payload.id_greenhouse,
        code=payload.code.strip().upper(),
        description=payload.description.strip() if payload.description else None
    )
    db.add(new_device)
    await db.flush()

    if payload.sensors:
        for s in payload.sensors:
            new_sensor = Sensor(
                id_device=new_device.id_device,
                id_sensor_type=s.id_sensor_type,
                code=s.code.strip().upper(),
                location=s.location.strip() if s.location else None
            )
            db.add(new_sensor)

    await db.commit()
    return await get_device_by_id(db, new_device.id_device)
# ============================================================
# 1. LISTAR DISPOSITIVOS CON CONSULTA ROBUSTA (SIN ERRORES 500)
# ============================================================
async def list_devices(
    db: AsyncSession,
    greenhouse_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0
):
    # Cargar únicamente la relación existente con sensores
    query = select(Device).options(
        selectinload(Device.sensors)
    )

    if greenhouse_id:
        query = query.where(Device.id_greenhouse == greenhouse_id)

    query = query.order_by(Device.registered_at.desc())

    # Contar total para paginación
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    # Ejecutar paginado
    result = await db.execute(query.limit(limit).offset(offset))
    devices = result.scalars().unique().all()

    items = []
    for d in devices:
        items.append({
            "id_device": d.id_device,
            "id_greenhouse": d.id_greenhouse,
            "id_pile": d.id_pile,
            "code": d.code,
            "description": d.description,
            "assigned_pile_code": None, # O la relación correspondiente si existe
            "sensors_count": len(d.sensors) if d.sensors else 0,
            "is_active": getattr(d, 'is_active', getattr(d, 'status', True)),
            "registered_at": d.registered_at
        })

    return {"items": items, "total": total}

# ============================================================
# 2. OBTENER DETALLE DE DISPOSITIVO
# ============================================================
async def get_device_by_id(db: AsyncSession, device_id: UUID):
    result = await db.execute(
        select(Device)
        .where(Device.id_device == device_id)
        .options(
            selectinload(Device.sensors).selectinload(Sensor.sensor_type)
        )
    )
    device = result.scalars().first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo IoT no encontrado"
        )

    return {
        "id_device": device.id_device,
        "id_greenhouse": device.id_greenhouse,
        "id_pile": device.id_pile,
        "code": device.code,
        "description": device.description,
        "assigned_pile_code": None,
        "sensors_count": len(device.sensors) if device.sensors else 0,
        "is_active": device.is_active,
        "registered_at": device.registered_at,
        "sensors": device.sensors
    }
# ============================================================
# 4. ACTUALIZAR DISPOSITIVO Y SENSORES
# ============================================================
async def update_device(db: AsyncSession, device_id: UUID, payload: DeviceUpdate):
    result = await db.execute(
        select(Device)
        .where(Device.id_device == device_id)
        .options(selectinload(Device.sensors))
    )
    device = result.scalars().first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo IoT no encontrado"
        )

    if payload.description is not None:
        device.description = payload.description.strip() if payload.description else None

    if payload.sensors is not None:
        await db.execute(delete(Sensor).where(Sensor.id_device == device_id))
        for s in payload.sensors:
            new_sensor = Sensor(
                id_device=device.id_device,
                id_sensor_type=s.id_sensor_type,
                code=s.code.strip().upper(),
                location=s.location.strip() if s.location else None
            )
            db.add(new_sensor)

    await db.commit()
    return await get_device_by_id(db, device_id)

# ============================================================
# 5. CAMBIAR ESTADO (ACTIVAR / DESACTIVAR)
# ============================================================
async def toggle_device_status(db: AsyncSession, device_id: UUID):
    result = await db.execute(select(Device).where(Device.id_device == device_id))
    device = result.scalars().first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo IoT no encontrado"
        )

    device.is_active = not device.is_active
    await db.commit()
    return await get_device_by_id(db, device_id)

# ============================================================
# 6. OBTENER CATÁLOGO DE TIPOS DE SENSORES
# ============================================================
async def get_sensor_types(db: AsyncSession):
    result = await db.execute(select(SensorType).order_by(SensorType.name.asc()))
    return result.scalars().all()