from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from schemas.user import UserUpdate, UserCreate, UpdateUserPayload
from mappers.user_mapper import (
    map_user_to_response,
    map_user_to_list_response,
    map_user_to_detail_response
)
from models.user import User
from models.role import Role
from models.assignment import Assignment
from models.greenhouse import Greenhouse
from core.security import hash_password

# Crear Usuario
async def create_user(db: AsyncSession, user_data: UserCreate):
    try:
        email = user_data.email.lower().strip()

        result = await db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"field": "email", "message": "El correo ya está registrado"}
            )

        result = await db.execute(
            select(Role).where(Role.id_role == user_data.id_role)
        )
        role = result.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol no existe"
            )

        hashed_password = hash_password(user_data.password)

        new_user = User(
            name=user_data.name.strip(),
            email=email,
            password_hash=hashed_password,
            id_role=user_data.id_role,
            is_active=True
        )

        db.add(new_user)
        await db.flush()

        if user_data.greenhouse_ids:
            for gh_id in user_data.greenhouse_ids:
                new_assignment = Assignment(
                    id_user=new_user.id_user,
                    id_greenhouse=gh_id
                )
                db.add(new_assignment)

        await db.commit()
        await db.refresh(new_user, attribute_names=["role", "assignments"])

        return map_user_to_response(new_user)

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear usuario"
        )

# Actualizar Usuario
async def update_user(db: AsyncSession, user_id: str, user_data: UpdateUserPayload):
    try:
        u_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        result = await db.execute(
            select(User)
            .where(User.id_user == u_uuid)
            .options(
                selectinload(User.role),
                selectinload(User.assignments)
            )
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user_data.email is not None:
            email = user_data.email.lower().strip()
            result = await db.execute(
                select(User).where(User.email == email, User.id_user != u_uuid)
            )
            if result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail={"field": "email", "message": "El correo ya está registrado"}
                )
            user.email = email

        if user_data.id_role is not None:
            result = await db.execute(
                select(Role).where(Role.id_role == user_data.id_role)
            )
            role = result.scalars().first()
            if not role:
                raise HTTPException(404, "El rol no existe")
            user.id_role = user_data.id_role

        if user_data.name is not None:
            user.name = user_data.name.strip()

        target_role = user_data.id_role if user_data.id_role is not None else user.id_role
        
        if user_data.greenhouse_ids is not None:
            await db.execute(
                delete(Assignment).where(Assignment.id_user == u_uuid)
            )
            
            if target_role != 1:
                for gh_id in user_data.greenhouse_ids:
                    gh_uuid = UUID(gh_id) if isinstance(gh_id, str) else gh_id
                    new_assignment = Assignment(
                        id_user=u_uuid,
                        id_greenhouse=gh_uuid
                    )
                    db.add(new_assignment)

        await db.commit()
        
        result_refreshed = await db.execute(
            select(User)
            .where(User.id_user == u_uuid)
            .options(
                selectinload(User.role),
                selectinload(User.assignments).selectinload(Assignment.greenhouse)
            )
        )
        user = result_refreshed.scalars().first()

        # Retornamos el mapper de detalle para que devuelva client_id y greenhouse_ids actualizados
        return map_user_to_detail_response(user)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print("ERROR CRITICO EN UPDATE_USER:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )

# Listar Usuarios
async def list_users(
    db: AsyncSession,
    client_id: UUID = None,
    search: str = None,
    limit: int = 5,
    offset: int = 0
):
    query = select(User).options(
        selectinload(User.role),
        selectinload(User.assignments)
    )

    if client_id:
        query = query.join(Assignment).join(Greenhouse).where(Greenhouse.id_client == client_id)

    if search:
        query = query.where(User.name.ilike(f"%{search.strip()}%"))

    # Ordenar por fecha de creación (del más reciente al más antiguo)
    query = query.order_by(User.created_at.desc())

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    users = result.scalars().unique().all()

    return {
        "items": [map_user_to_list_response(user) for user in users],
        "total": total
    }

# Activar / Desactivar Usuario
async def toggle_user_status(db: AsyncSession, user_id):
    result = await db.execute(
        select(User)
        .where(User.id_user == user_id)
        .options(
            selectinload(User.role),
            selectinload(User.assignments)
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)

    return map_user_to_response(user)

# Obtener Usuario por ID (Detalle)
async def get_user_by_id(db: AsyncSession, user_id):
    result = await db.execute(
        select(User)
        .where(User.id_user == user_id)
        .options(
            selectinload(User.role),
            selectinload(User.assignments).selectinload(Assignment.greenhouse)
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return map_user_to_detail_response(user)