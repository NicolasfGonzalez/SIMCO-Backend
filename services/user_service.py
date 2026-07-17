from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from schemas.user import UserUpdate
from mappers.user_mapper import map_user_to_response
from models.user import User
from models.role import Role
from models.client import Client
from schemas.user import UserCreate
from core.security import hash_password
from mappers.user_mapper import map_user_to_list_response


# Crear Usuario 

async def create_user(db: AsyncSession, user_data: UserCreate):

    try:
        # 1. Normalizar email
        email = user_data.email.lower().strip()

        # 2. Validar email único
        result = await db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado"
            )

        # 3. Validar rol
        result = await db.execute(
            select(Role).where(Role.id_role == user_data.id_role)
        )
        role = result.scalars().first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol no existe"
            )

        # 4. Validar cliente
        result = await db.execute(
            select(Client).where(Client.id_client == user_data.id_client)
        )
        client = result.scalars().first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El cliente no existe"
            )

        # 5. Hash password
        hashed_password = hash_password(user_data.password)

        # 6. Crear usuario
        new_user = User(
            name=user_data.name.strip(),
            email=email,
            password_hash=hashed_password,
            id_role=user_data.id_role,
            id_client=user_data.id_client,
            is_active=True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        await db.refresh(new_user, attribute_names=["role", "client"])

        #  7. Usar mapper 
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
async def update_user(
    db: AsyncSession,
    user_id,
    user_data: UserUpdate
):

    try:
        # 1. Buscar usuario
        result = await db.execute(
            select(User).where(User.id_user == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # 2. Validar email único (si viene)
        if user_data.email:
            email = user_data.email.lower().strip()

            result = await db.execute(
                select(User).where(User.email == email, User.id_user != user_id)
            )
            if result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail="El correo ya está registrado"
                )

            user.email = email

        # 3. Validar rol
        if user_data.id_role:
            result = await db.execute(
                select(Role).where(Role.id_role == user_data.id_role)
            )
            role = result.scalars().first()

            if not role:
                raise HTTPException(404, "El rol no existe")

            user.id_role = user_data.id_role

        # 4. Validar cliente
        if user_data.id_client:
            result = await db.execute(
                select(Client).where(Client.id_client == user_data.id_client)
            )
            client = result.scalars().first()

            if not client:
                raise HTTPException(404, "El cliente no existe")

            user.id_client = user_data.id_client

        # 5. Otros campos
        if user_data.name:
            user.name = user_data.name.strip()

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        await db.commit()
        await db.refresh(user)

        # cargar relaciones
        await db.refresh(user, attribute_names=["role", "client"])

        return map_user_to_response(user)

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar usuario"
        )

# Listar Usuarios
async def list_users(db: AsyncSession, client_id, limit: int, offset: int):

    #  SI NO VIENE client_id → TOMAMOS EL PRIMERO
    if client_id is None:
        result_client = await db.execute(select(Client).limit(1))
        client = result_client.scalars().first()

        if not client:
            return []

        client_id = client.id_client

    #  CONSULTA PRINCIPAL
    result = await db.execute(
        select(User)
        .where(User.id_client == client_id)
        .options(selectinload(User.role))
        .limit(limit)
        .offset(offset)
    )

    users = result.scalars().all()

    return [map_user_to_list_response(user) for user in users]


# Desactivar / Activar Usuario
async def toggle_user_status(db: AsyncSession, user_id):
    result = await db.execute(
        select(User)
        .where(User.id_user == user_id)
        .options(
            selectinload(User.role),
            selectinload(User.client)
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.is_active = not user.is_active

    await db.commit()
    await db.refresh(user)

    return map_user_to_response(user)