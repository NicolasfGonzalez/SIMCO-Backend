from fastapi import APIRouter
from app.api.v1.endpoints import items

api_router = APIRouter()

# Aquí vas colgando todos los endpoints que crees a futuro
api_router.include_router(items.router, prefix="/items", tags=["items"])