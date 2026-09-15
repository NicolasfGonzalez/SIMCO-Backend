from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


from models.client import Client
from schemas.client_schema import ClientCreate, ClientUpdate
from mappers.client_mapper import map_client_to_response, map_client_to_basic_response
from mappers.client_mapper import map_clients_to_basic_response

async def list_clients_basic(db):
    result = await db.execute(select(Client))
    clients = result.scalars().all()

    return map_clients_to_basic_response(clients)

# 1. Traer todos los clientes (Para el Selector/Dropdown del Frontend)
async def get_all_clients_basic(db: AsyncSession):
    result = await db.execute(
        select(Client).order_by(Client.name.asc())
    )
    clients = result.scalars().all()
    return [map_client_to_basic_response(c) for c in clients]

# 2. Listar Clientes (Con Paginación y Búsqueda)
async def list_clients(
    db: AsyncSession,
    search: str = None,
    limit: int = 10,
    offset: int = 0
):
    query = select(Client)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Client.name.ilike(search_pattern),
                Client.email.ilike(search_pattern),
                Client.phone.ilike(search_pattern)
            )
        )

    query = query.order_by(Client.created_at.desc())

    # Total de registros
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    clients = result.scalars().all()

    return {
        "items": [map_client_to_response(c) for c in clients],
        "total": total
    }

# 3. Crear Cliente
async def create_client(db: AsyncSession, client_data: ClientCreate):
    if client_data.email:
        email_clean = client_data.email.lower().strip()
        existing = await db.execute(select(Client).where(Client.email == email_clean))
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya pertenece a otro cliente"
            )
    else:
        email_clean = None

    new_client = Client(
        name=client_data.name.strip(),
        email=email_clean,
        phone=client_data.phone.strip() if client_data.phone else None
    )

    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)

    return map_client_to_response(new_client)

# 4. Obtener por ID
async def get_client_by_id(db: AsyncSession, client_id: UUID):
    result = await db.execute(select(Client).where(Client.id_client == client_id))
    client = result.scalars().first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return map_client_to_response(client)

# 5. Actualizar Cliente
async def update_client(db: AsyncSession, client_id: UUID, client_data: ClientUpdate):
    result = await db.execute(select(Client).where(Client.id_client == client_id))
    client = result.scalars().first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if client_data.email:
        email_clean = client_data.email.lower().strip()
        existing = await db.execute(
            select(Client).where(Client.email == email_clean, Client.id_client != client_id)
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya pertenece a otro cliente"
            )
    
    update_dict = client_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "email" and value:
            setattr(client, key, value.lower().strip())
        elif key == "name" and value:
            setattr(client, key, value.strip())
        else:
            setattr(client, key, value)

    await db.commit()
    await db.refresh(client)

    return map_client_to_response(client)