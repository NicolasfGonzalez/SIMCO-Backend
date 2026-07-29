from sqlalchemy import select
from models.client import Client
from mappers.client_mapper import map_clients_to_basic_response

async def list_clients_basic(db):
    result = await db.execute(select(Client))
    clients = result.scalars().all()

    return map_clients_to_basic_response(clients)