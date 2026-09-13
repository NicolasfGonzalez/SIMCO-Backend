from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from core.database import get_db
from schemas.greenhouse_schema import GreenhouseListResponse
from services.greenhouse_service import get_greenhouses_by_client

router = APIRouter(prefix="/greenhouses", tags=["Greenhouses"])

@router.get("/", response_model=GreenhouseListResponse)
async def list_greenhouses_endpoint(
    client_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    if client_id:
        greenhouses = await get_greenhouses_by_client(db, client_id)
    else:
        greenhouses = []
    return {"items": greenhouses}