
from models.greenhouse import Greenhouse 
from schemas.greenhouse_schema import GreenhouseBasicResponse
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from models.greenhouse import Greenhouse
from models.assignment import Assignment # Importamos la tabla intermedia
from schemas.greenhouse_schema import GreenhouseCreate, GreenhouseUpdate
from mappers.greenhouse_mapper import (
    map_greenhouse_to_list_response, 
    map_greenhouse_to_detail_response   
)

async def get_greenhouses_by_client(
    db: AsyncSession,
    client_id: UUID
) -> list[GreenhouseBasicResponse]:

    result = await db.execute(
        select(
            Greenhouse.id_greenhouse,
            Greenhouse.name
        )
        .where(
            Greenhouse.id_client == client_id
        )
        .order_by(
            Greenhouse.name.asc()
        )
    )

    greenhouses = result.all()

    return [
        GreenhouseBasicResponse(
            id_greenhouse=greenhouse.id_greenhouse,
            name=greenhouse.name
        )
        for greenhouse in greenhouses
    ]

# ==========================================
# Crear Invernadero
# ==========================================
async def create_greenhouse(db: AsyncSession, gh_data: GreenhouseCreate):
    new_gh = Greenhouse(
        id_client=gh_data.id_client,
        name=gh_data.name.strip(),
        location=gh_data.location.strip(),
        latitude=gh_data.latitude,
        longitude=gh_data.longitude,
        is_active=True
    )
    
    db.add(new_gh)
    await db.commit()
    # Refrescamos cargando la relación vacía de assignments para el mapper
    await db.refresh(new_gh, attribute_names=["assignments"])
    
    return map_greenhouse_to_detail_response(new_gh)

# ==========================================
# Listar Invernaderos (Con filtro y paginación)
# ==========================================
async def list_greenhouses(
    db: AsyncSession,
    client_id: UUID = None,
    limit: int = 10,
    offset: int = 0
):
    # Cargamos la tabla intermedia y, anidado a ella, el usuario para obtener su nombre
    query = select(Greenhouse).options(
        selectinload(Greenhouse.assignments).selectinload(Assignment.user)
    )

    if client_id:
        query = query.where(Greenhouse.id_client == client_id)

    # Ordenamos por orden de creación (Los más nuevos primero)
    query = query.order_by(Greenhouse.created_at.desc())

    # Total para paginación
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    greenhouses = result.scalars().unique().all()

    return {
        "items": [map_greenhouse_to_list_response(gh) for gh in greenhouses],
        "total": total
    }

# ==========================================
# Obtener Invernadero por ID
# ==========================================
async def get_greenhouse_by_id(db: AsyncSession, gh_id: UUID):
    result = await db.execute(
        select(Greenhouse)
        .where(Greenhouse.id_greenhouse == gh_id)
        .options(selectinload(Greenhouse.assignments).selectinload(Assignment.user))
    )
    gh = result.scalars().first()
    
    if not gh:
        raise HTTPException(status_code=404, detail="Invernadero no encontrado")
        
    return map_greenhouse_to_detail_response(gh)

# ==========================================
# Actualizar Invernadero
# ==========================================
async def update_greenhouse(db: AsyncSession, gh_id: UUID, gh_data: GreenhouseUpdate):
    result = await db.execute(
        select(Greenhouse)
        .where(Greenhouse.id_greenhouse == gh_id)
        .options(selectinload(Greenhouse.assignments).selectinload(Assignment.user))
    )
    gh = result.scalars().first()
    
    if not gh:
        raise HTTPException(status_code=404, detail="Invernadero no encontrado")

    update_dict = gh_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(gh, key, value)

    await db.commit()
    await db.refresh(gh)
    
    return map_greenhouse_to_detail_response(gh)

# ==========================================
# Activar / Desactivar Invernadero
# ==========================================
async def toggle_greenhouse_status(db: AsyncSession, gh_id: UUID):
    result = await db.execute(
        select(Greenhouse)
        .where(Greenhouse.id_greenhouse == gh_id)
        .options(selectinload(Greenhouse.assignments).selectinload(Assignment.user))
    )
    gh = result.scalars().first()
    
    if not gh:
        raise HTTPException(status_code=404, detail="Invernadero no encontrado")

    gh.is_active = not gh.is_active
    
    await db.commit()
    await db.refresh(gh)
    
    return map_greenhouse_to_detail_response(gh)