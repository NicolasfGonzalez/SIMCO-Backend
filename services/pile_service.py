from uuid import UUID
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from models.pile import Pile
from models.device import Device
from schemas.pile_schema import PileCreate, PileUpdate
from mappers.pile_mapper import map_pile_to_detail_response, map_pile_to_list_response


# ============================================================
# CREAR PILA (PostgreSQL + MongoDB Atlas)
# ============================================================
async def create_pile(
    db: AsyncSession, 
    mongo_db: AsyncIOMotorDatabase, 
    payload: PileCreate
):
    # Validar duplicados por código
    existing = await db.execute(
        select(Pile).where(Pile.code == payload.code.strip().upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La pila con código '{payload.code}' ya se encuentra registrada"
        )

    # Sanear fecha para PostgreSQL (TIMESTAMP WITHOUT TIME ZONE)
    clean_process_date = payload.process_start_date
    if clean_process_date.tzinfo is not None:
        clean_process_date = clean_process_date.replace(tzinfo=None)

    # 1. Insertar en PostgreSQL
    new_pile = Pile(
        id_greenhouse=payload.id_greenhouse,
        code=payload.code.strip().upper(),
        name=payload.name.strip() if payload.name else None,
        process_start_date=clean_process_date
    )
    db.add(new_pile)
    await db.commit()
    
    # 2. Re-consultar la pila con relaciones precargadas para el mapper
    result = await db.execute(
        select(Pile)
        .where(Pile.id_pile == new_pile.id_pile)
        .options(selectinload(Pile.devices))
    )
    created_pile = result.scalars().first()

    # 3. Guardar metadatos en MongoDB Atlas (Colección "compost_piles")
    mongo_doc = {
        "pile_code": created_pile.code,
        "location": payload.location or "",
        "start_date": payload.process_start_date.isoformat(),
        "estimated_end_date": payload.estimated_end_date.isoformat() if payload.estimated_end_date else None,
        "status": "Activa",
        "base_material": payload.base_material or "",
        "notes": payload.notes or ""
    }

    if mongo_db is not None:
        try:
            await mongo_db["compost_piles"].update_one(
                {"pile_code": created_pile.code},
                {"$set": mongo_doc},
                upsert=True
            )
        except Exception as e:
            print(f"Error registrando en Mongo ('compost_piles'): {e}")

    # 4. Retornar la respuesta totalmente serializada
    return map_pile_to_detail_response(created_pile, mongo_doc, None)
# ============================================================
# LISTAR PILAS PAGINADAS
# ============================================================
async def list_piles(
    db: AsyncSession,
    mongo_db: AsyncIOMotorDatabase = None,  # 👈 Agregado para aceptar la inyección de FastAPI sin fallar
    greenhouse_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0
):
    query = select(Pile).options(selectinload(Pile.devices))

    # Filtrar por Invernadero
    if greenhouse_id:
        query = query.where(Pile.id_greenhouse == greenhouse_id)

    query = query.order_by(Pile.created_at.desc())

    # Total de registros para la paginación del frontend
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    # Ejecutar consulta paginada
    result = await db.execute(query.limit(limit).offset(offset))
    piles = result.scalars().unique().all()

    return {
        "items": [map_pile_to_list_response(pile) for pile in piles],
        "total": total
    }
# ============================================================
# OBTENER DETALLE POR ID
# ============================================================
async def get_pile_by_id(
    db: AsyncSession,
    mongo_db: AsyncIOMotorDatabase,
    pile_id: UUID
):
    result = await db.execute(
        select(Pile)
        .where(Pile.id_pile == pile_id)
        .options(selectinload(Pile.devices))
    )
    pile = result.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila de compostaje no encontrada"
        )

    # Consultar metadatos en MongoDB Atlas
    mongo_doc = None
    latest_telemetry = None

    if mongo_db is not None:
        mongo_doc = await mongo_db["piles"].find_one({"pile_code": pile.code})
        latest_telemetry = await mongo_db["telemetry"].find_one(
            {"metadata.pile_code": pile.code},
            sort=[("timestamp", -1)]
        )

    return map_pile_to_detail_response(pile, mongo_doc, latest_telemetry)


# ============================================================
# ACTUALIZAR PILA
# ============================================================
async def update_pile(
    db: AsyncSession,
    mongo_db: AsyncIOMotorDatabase,
    pile_id: UUID,
    payload: PileUpdate
):
    result = await db.execute(
        select(Pile)
        .where(Pile.id_pile == pile_id)
        .options(selectinload(Pile.devices))
    )
    pile = result.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila de compostaje no encontrada"
        )

    # Actualizar campos relacionales
    if payload.name is not None:
        pile.name = payload.name.strip()
    if payload.process_start_date is not None:
        pile.process_start_date = payload.process_start_date

    await db.commit()
    await db.refresh(pile)

    # Actualizar metadatos en Mongo
    mongo_update = {}
    if payload.location is not None:
        mongo_update["location"] = payload.location
    if payload.estimated_end_date is not None:
        mongo_update["estimated_end_date"] = payload.estimated_end_date.isoformat()
    if payload.status is not None:
        mongo_update["status"] = payload.status
    if payload.base_material is not None:
        mongo_update["base_material"] = payload.base_material
    if payload.notes is not None:
        mongo_update["notes"] = payload.notes

    mongo_doc = None
    if mongo_db is not None:
        if mongo_update:
            await mongo_db["piles"].update_one(
                {"pile_code": pile.code},
                {"$set": mongo_update},
                upsert=True
            )
        mongo_doc = await mongo_db["piles"].find_one({"pile_code": pile.code})

    return map_pile_to_detail_response(pile, mongo_doc, None)


# ============================================================
# ASIGNAR DISPOSITIVO IOT
# ============================================================
async def assign_device_to_pile(
    db: AsyncSession,
    pile_id: UUID,
    device_code: str
):
    result_pile = await db.execute(select(Pile).where(Pile.id_pile == pile_id))
    pile = result_pile.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila no encontrada"
        )

    result_device = await db.execute(select(Device).where(Device.code == device_code))
    device = result_device.scalars().first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El dispositivo {device_code} no está registrado"
        )

    device.id_pile = pile.id_pile
    await db.commit()

    return {"message": f"Dispositivo {device_code} asignado con éxito a la pila {pile.code}"}