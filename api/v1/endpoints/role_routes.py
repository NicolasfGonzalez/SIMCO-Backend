from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.role_schema import RoleOut
from services.role_service import get_all_roles

# Endpoints para listar todos los roles
router = APIRouter(prefix="/roles", tags=["Roles"])
@router.get("/", response_model=list[RoleOut])
async def get_roles(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_roles(db)