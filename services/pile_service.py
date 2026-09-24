from uuid import UUID
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from models.pile import Pile
from models.device import Device
from schemas.pile_schema import PileCreate, PileUpdate

# Colección estándar 
MONGO_COLLECTION = "compost_piles"

# servicio para crear una pila de compostaje
async def create_pile(db: AsyncSession, mongo_db, payload: PileCreate) -> dict:
    code_upper = payload.code.strip().upper()

    # Verificar existencia previa
    existing = await db.execute(select(Pile).where(Pile.code == code_upper))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una pila de compostaje con el código '{code_upper}'."
        )

    # Normalizar fechas a Naive UTC (sin zona horaria) para PostgreSQL
    start_date_naive = payload.process_start_date.replace(tzinfo=None) if payload.process_start_date else datetime.utcnow()
    end_date_naive = payload.estimated_end_date.replace(tzinfo=None) if payload.estimated_end_date else None

    # Guardar entidad en PostgreSQL
    new_pile = Pile(
        id_greenhouse=payload.id_greenhouse,
        code=code_upper,
        name=payload.name.strip() if payload.name else None,
        process_start_date=start_date_naive,
        estimated_end_date=end_date_naive,
        status="Activa",
    )
    db.add(new_pile)
    await db.commit()

    # Guardar metadatos en MongoDB Atlas
    if mongo_db is not None:
        try:
            await mongo_db[MONGO_COLLECTION].insert_one({
                "pile_code": code_upper,
                "status": "Activa",
                "start_date": start_date_naive.isoformat(),
                "estimated_end_date": end_date_naive.isoformat() if end_date_naive else None,
                "base_material": getattr(payload, "base_material", "") or "",
                "notes": getattr(payload, "notes", "") or "",
                "created_at": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            print(f"Error al guardar metadatos en MongoDB: {e}")

    return await get_pile_by_id(db, mongo_db, new_pile.id_pile)


async def list_piles(
    db: AsyncSession,
    mongo_db,
    greenhouse_id: Optional[UUID] = None,
    limit: int = 4,   
    offset: int = 0,  
) -> dict:
    query = select(Pile).options(selectinload(Pile.devices))

    if greenhouse_id:
        query = query.where(Pile.id_greenhouse == greenhouse_id)

    query = query.order_by(Pile.created_at.desc())

    # Obtener el TOTAL REAL de pilas para que el frontend calcule el número de páginas
    total_query = select(func.count()).select_from(
        select(Pile.id_pile).where(Pile.id_greenhouse == greenhouse_id).subquery()
        if greenhouse_id else select(Pile.id_pile).subquery()
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    piles = result.scalars().all()

    items = []
    for pile in piles:
        assigned_device = pile.devices[0].code if pile.devices else None

        current_status = getattr(pile, "status", "Activa")
        if mongo_db is not None:
            doc = await mongo_db["compost_piles"].find_one({"pile_code": pile.code}, {"status": 1})
            if doc and "status" in doc:
                current_status = doc["status"]

        items.append({
            "id_pile": pile.id_pile,
            "id_greenhouse": pile.id_greenhouse,
            "code": pile.code,
            "name": pile.name,
            "process_start_date": pile.process_start_date,
            "estimated_end_date": getattr(pile, "estimated_end_date", None),
            "status": current_status,
            "created_at": pile.created_at,
            "assigned_device_code": assigned_device,
        })

    return {"items": items, "total": total}

# service para obtener detalles de una pila específica por su ID
async def get_pile_by_id(db: AsyncSession, mongo_db, pile_id: UUID) -> dict:
    result = await db.execute(
        select(Pile)
        .where(Pile.id_pile == pile_id)
        .options(selectinload(Pile.devices))
    )
    pile = result.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila de compostaje no encontrada."
        )

    assigned_device = pile.devices[0].code if pile.devices else None

    mongo_doc = None
    if mongo_db is not None:
        mongo_doc = await mongo_db[MONGO_COLLECTION].find_one({"pile_code": pile.code})

    return {
        "id_pile": pile.id_pile,
        "id_greenhouse": pile.id_greenhouse,
        "code": pile.code,
        "name": pile.name,
        "process_start_date": pile.process_start_date,
        "estimated_end_date": getattr(pile, "estimated_end_date", None),
        "status": mongo_doc.get("status", getattr(pile, "status", "Activa")) if mongo_doc else getattr(pile, "status", "Activa"),
        "base_material": mongo_doc.get("base_material", "") if mongo_doc else "",
        "notes": mongo_doc.get("notes", "") if mongo_doc else "",
        "created_at": pile.created_at,
        "assigned_device_code": assigned_device,
    }

# service para actualizar los detalles de una pila específica
async def update_pile(db: AsyncSession, mongo_db, pile_id: UUID, payload: PileUpdate) -> dict:
    result = await db.execute(
        select(Pile).where(Pile.id_pile == pile_id)
    )
    pile = result.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila de compostaje no encontrada."
        )

    #  Actualización en PostgreSQL con conversión estricta de fechas Naive UTC
    if payload.name is not None:
        pile.name = payload.name.strip()
    if payload.process_start_date is not None:
        pile.process_start_date = payload.process_start_date.replace(tzinfo=None)
    if payload.estimated_end_date is not None:
        pile.estimated_end_date = payload.estimated_end_date.replace(tzinfo=None)
    if payload.status is not None:
        pile.status = payload.status

    # Regla de Liberación de Hardware
    if payload.status in ["Finalizada", "Archivada"]:
        devices_assigned = await db.execute(
            select(Device).where(Device.id_pile == pile_id)
        )
        for dev in devices_assigned.scalars().all():
            dev.id_pile = None

    await db.commit()

    # Sincronización en MongoDB Atlas en la colección 'compost_piles'
    if mongo_db is not None:
        update_doc = {}
        if payload.status is not None:
            update_doc["status"] = payload.status
        if payload.process_start_date is not None:
            update_doc["start_date"] = payload.process_start_date.replace(tzinfo=None).isoformat()
        if payload.estimated_end_date is not None:
            update_doc["estimated_end_date"] = payload.estimated_end_date.replace(tzinfo=None).isoformat()
        if payload.base_material is not None:
            update_doc["base_material"] = payload.base_material.strip()
        if payload.notes is not None:
            update_doc["notes"] = payload.notes.strip()

        if update_doc:
            await mongo_db[MONGO_COLLECTION].update_one(
                {"pile_code": pile.code},
                {"$set": update_doc},
                upsert=True
            )

    return await get_pile_by_id(db, mongo_db, pile_id)

# service para asignar un dispositivo a una pila específica
async def assign_device_to_pile(db: AsyncSession, mongo_db, pile_id: UUID, device_code: Optional[str] = None) -> dict:
    result = await db.execute(select(Pile).where(Pile.id_pile == pile_id))
    pile = result.scalars().first()

    if not pile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pila de compostaje no encontrada."
        )

    previous_devices = await db.execute(select(Device).where(Device.id_pile == pile_id))
    for dev in previous_devices.scalars().all():
        dev.id_pile = None

    if device_code and device_code.strip():
        dev_result = await db.execute(
            select(Device).where(Device.code == device_code.strip().upper())
        )
        device = dev_result.scalars().first()

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El dispositivo '{device_code}' no existe."
            )

        device.id_pile = pile_id

    await db.commit()

    return await get_pile_by_id(db, mongo_db, pile_id)