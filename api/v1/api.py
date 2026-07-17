from fastapi import APIRouter
from api.v1.endpoints import items
from api.v1.endpoints.user_routes import router as user_router

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(user_router)
