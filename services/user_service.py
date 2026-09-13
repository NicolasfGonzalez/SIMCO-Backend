from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status

from schemas.user import UserUpdate, UserCreate

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

# CREAR USUARIO
async def create_user(
    db: AsyncSession,
    user_data: UserCreate
):

    # Validar correo

    result = await db.execute(
        select(User)
        .where(User.email == user_data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )

    # Validar rol

    result = await db.execute(
        select(Role)
        .where(Role.id_role == user_data.id_role)
    )

    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol seleccionado no existe"
        )

    # Crear usuario
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        id_role=user_data.id_role,
        is_active=True
    )

    db.add(new_user)

    await db.flush()

    # Crear asignaciones
    greenhouse_ids = user_data.greenhouse_ids or []

    # ADMIN no necesita asignaciones
    if user_data.id_role != 1:

        for greenhouse_id in greenhouse_ids:

            # Validar que el invernadero exista
            result_greenhouse = await db.execute(
                select(
                    Greenhouse.id_greenhouse
                )
                .where(
                    Greenhouse.id_greenhouse == greenhouse_id
                )
            )

            greenhouse_exists = (
                result_greenhouse.scalar_one_or_none()
            )

            if not greenhouse_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"El invernadero "
                        f"{greenhouse_id} no existe"
                    )
                )

            assignment = Assignment(
                id_user=new_user.id_user,
                id_greenhouse=greenhouse_id
            )

            db.add(assignment)

    # Guardar
    await db.commit()

    result = await db.execute(
        select(User)
        .where(
            User.id_user == new_user.id_user
        )
        .options(
            selectinload(User.role),
            selectinload(User.assignments)
        )
    )

    new_user = result.scalars().first()

    return map_user_to_response(new_user)

# ACTUALIZAR USUARIO
async def update_user(
    db: AsyncSession,
    user_id: UUID,
    user_data: UserUpdate
):

    # Buscar usuario
    result = await db.execute(
        select(User)
        .where(
            User.id_user == user_id
        )
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

    # Validar correo
    if (
        user_data.email
        and user_data.email != user.email
    ):

        result_email = await db.execute(
            select(User)
            .where(
                User.email == user_data.email,
                User.id_user != user_id
            )
        )

        existing_email = (
            result_email.scalar_one_or_none()
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El correo electrónico "
                    "ya está registrado"
                )
            )

        user.email = user_data.email

    # Actualizar nombre
    if user_data.name is not None:
        user.name = user_data.name

    # Actualizar rol
    if user_data.id_role is not None:

        result_role = await db.execute(
            select(Role)
            .where(
                Role.id_role == user_data.id_role
            )
        )

        role = result_role.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol seleccionado no existe"
            )

        user.id_role = user_data.id_role

    # Determinar rol final
    target_role = (
        user_data.id_role
        if user_data.id_role is not None
        else user.id_role
    )

    if user_data.greenhouse_ids is not None:

        # Eliminar asignaciones actuales
        await db.execute(
            delete(Assignment)
            .where(
                Assignment.id_user == user.id_user
            )
        )

        # ADMIN no necesita invernaderos
        if target_role != 1:

            for greenhouse_id in (
                user_data.greenhouse_ids
            ):

                # Validar existencia
                result_greenhouse = await db.execute(
                    select(
                        Greenhouse.id_greenhouse
                    )
                    .where(
                        Greenhouse.id_greenhouse
                        == greenhouse_id
                    )
                )

                greenhouse_exists = (
                    result_greenhouse
                    .scalar_one_or_none()
                )

                if not greenhouse_exists:
                    raise HTTPException(
                        status_code=(
                            status.HTTP_404_NOT_FOUND
                        ),
                        detail=(
                            f"El invernadero "
                            f"{greenhouse_id} "
                            f"no existe"
                        )
                    )

                assignment = Assignment(
                    id_user=user.id_user,
                    id_greenhouse=greenhouse_id
                )

                db.add(assignment)

    # Guardar cambios
    await db.commit()

    result_refreshed = await db.execute(
        select(User)
        .where(
            User.id_user == user.id_user
        )
        .options(
            selectinload(User.role),
            selectinload(User.assignments)
        )
    )

    user = result_refreshed.scalars().first()

    # Obtener IDs de invernaderos

    greenhouse_ids = [
        assignment.id_greenhouse
        for assignment in user.assignments
    ] if user.assignments else []

    client_id = None

    if greenhouse_ids:

        result_client = await db.execute(
            select(
                Greenhouse.id_client
            )
            .where(
                Greenhouse.id_greenhouse.in_(
                    greenhouse_ids
                )
            )
            .limit(1)
        )

        client_id = (
            result_client.scalar_one_or_none()
        )

    # Respuesta

    return map_user_to_detail_response(
        user,
        client_id=client_id
    )


# LISTAR USUARIOS
async def list_users(
    db: AsyncSession,
    client_id: UUID | None = None,
    search: str | None = None,
    limit: int = 5,
    offset: int = 0
):

    query = select(User).options(
        selectinload(User.role),
        selectinload(User.assignments)
    )

    # Filtrar por cliente
    if client_id:

        query = (
            query
            .join(Assignment)
            .join(Greenhouse)
            .where(
                Greenhouse.id_client == client_id
            )
        )

    # Buscar por nombre
    if search:

        query = query.where(
            User.name.ilike(
                f"%{search.strip()}%"
            )
        )

    # Ordenar
    query = query.order_by(
        User.created_at.desc()
    )

    # Total
    total_result = await db.execute(
        select(
            func.count()
        ).select_from(
            query.subquery()
        )
    )

    total = (
        total_result.scalar()
        or 0
    )

    # Paginación
    result = await db.execute(
        query
        .limit(limit)
        .offset(offset)
    )

    users = (
        result.scalars()
        .unique()
        .all()
    )

    # Respuesta
    return {
        "items": [
            map_user_to_list_response(user)
            for user in users
        ],
        "total": total
    }


# CAMBIAR ESTADO
async def toggle_user_status(
    db: AsyncSession,
    user_id: UUID
):

    # Buscar usuario
    result = await db.execute(
        select(User)
        .where(
            User.id_user == user_id
        )
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

    # Cambiar estado
    user.is_active = not user.is_active

    await db.commit()

    # Recargar
    result = await db.execute(
        select(User)
        .where(
            User.id_user == user_id
        )
        .options(
            selectinload(User.role),
            selectinload(User.assignments)
        )
    )
    user = result.scalars().first()

    return map_user_to_response(user)


# OBTENER USUARIO POR ID
async def get_user_by_id(
    db: AsyncSession,
    user_id: UUID
):
    # Buscar usuario
    result = await db.execute(
        select(User)
        .where(
            User.id_user == user_id
        )
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

    # Obtener greenhouse_ids
    greenhouse_ids = [
        assignment.id_greenhouse
        for assignment in user.assignments
    ] if user.assignments else []

    # Obtener client_id
    client_id = None

    if greenhouse_ids:

        result_client = await db.execute(
            select(
                Greenhouse.id_client
            )
            .where(
                Greenhouse.id_greenhouse.in_(
                    greenhouse_ids
                )
            )
            .limit(1)
        )

        client_id = (
            result_client.scalar_one_or_none()
        )

    # Respuesta
    return map_user_to_detail_response(
        user,
        client_id=client_id
    )