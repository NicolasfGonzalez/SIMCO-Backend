from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from models.greenhouse import Greenhouse # Asegúrate de importar tu modelo exacto
from schemas.greenhouse_schema import GreenhouseBasicResponse

async def get_greenhouses_by_client(db: AsyncSession, client_id: UUID) -> list[GreenhouseBasicResponse]:
    query = (
        select(Greenhouse)
        .where(Greenhouse.id_client == client_id)
        .order_by(Greenhouse.name.asc())
    )
    
    result = await db.execute(query)
    greenhouses = result.scalars().all()
    
    return greenhouses