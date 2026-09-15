from uuid import UUID
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from sqlalchemy import delete

from models.greenhouse import Greenhouse
from models.assignment import Assignment
from schemas.greenhouse_schema import GreenhouseCreate, GreenhouseUpdate, GreenhouseBasicResponse
from mappers.greenhouse_mapper import (
    map_greenhouse_to_list_response,
    map_greenhouse_to_detail_response
)
from models.assignment import Assignment

#  Servicio para listar invernaderos segun el cliente
async def get_greenhouses_by_client(db: AsyncSession, client_id: UUID) -> list[GreenhouseBasicResponse]:
    result = await db.execute(
        select(Greenhouse.id_greenhouse, Greenhouse.name)
        .where(Greenhouse.id_client == client_id)
        .order_by(Greenhouse.name.asc())
    )
    return [
        GreenhouseBasicResponse(id_greenhouse=row.id_greenhouse, name=row.name)
        for row in result.all()
    ]

# Servicio para crear un invernadero
async def create_greenhouse(db: AsyncSession, gh_data: GreenhouseCreate):
    new_gh = Greenhouse(
        id_client=gh_data.id_client,
        name=gh_data.name.strip(),
        address=gh_data.address.strip(),
        latitude=gh_data.latitude,
        longitude=gh_data.longitude,
        is_active=True
    )
    db.add(new_gh)
    await db.commit()
    await db.refresh(new_gh, attribute_names=["assignments"])
    return map_greenhouse_to_detail_response(new_gh)

# Servicio para listar invernaderos con paginación y filtrado
async def list_greenhouses(db: AsyncSession, client_id: Optional[UUID] = None, limit: int = 50, offset: int = 0):
    query = select(Greenhouse).options(
        selectinload(Greenhouse.assignments).selectinload(Assignment.user)
    )
    
    if client_id:
        query = query.where(Greenhouse.id_client == client_id)

    query = query.order_by(Greenhouse.created_at.desc())

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    greenhouses = result.scalars().unique().all()

    return {
        "items": [map_greenhouse_to_list_response(gh) for gh in greenhouses],
        "total": total
    }

# Servicio para obtener un invernadero por su ID
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

# Servicio para actualizar un invernadero
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

# Servicio para cambiar el estado de un invernadero 
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

# Servicio para asignar usuarios a un invernadero
async def assign_users_to_greenhouse(db: AsyncSession, gh_id: UUID, user_ids: list[UUID]):
    # Validar existencia
    result = await db.execute(
        select(Greenhouse).where(Greenhouse.id_greenhouse == gh_id)
    )
    gh = result.scalars().first()
    
    if not gh:
        raise HTTPException(status_code=404, detail="Invernadero no encontrado")

    # Limpiar asignaciones anteriores
    await db.execute(
        delete(Assignment).where(Assignment.id_greenhouse == gh_id)
    )

    # Crear las nuevas asignaciones
    if user_ids:
        new_assignments = [
            Assignment(id_user=uid, id_greenhouse=gh_id) for uid in user_ids
        ]
        db.add_all(new_assignments)

    # Confirmar transacción
    await db.commit()
    
    # Volver a consultar el invernadero con las relaciones recién creadas
    updated_result = await db.execute(
        select(Greenhouse)
        .where(Greenhouse.id_greenhouse == gh_id)
        .options(selectinload(Greenhouse.assignments).selectinload(Assignment.user))
    )
    updated_gh = updated_result.scalars().first()

    # Retornar al frontend
    return map_greenhouse_to_detail_response(updated_gh)