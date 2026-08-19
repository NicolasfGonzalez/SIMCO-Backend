from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.client_service import list_clients_basic
from schemas.client_schema import ClientBasicResponse
from typing import List

# Endpoints para listar todos los clientes
router = APIRouter(prefix="/clients", tags=["Clients"])
@router.get("/basic", response_model=List[ClientBasicResponse])
async def get_clients_basic(db: AsyncSession = Depends(get_db)):
    return await list_clients_basic(db)