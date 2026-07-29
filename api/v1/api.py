from fastapi import APIRouter
from api.v1.endpoints import items
from api.v1.endpoints.user_routes import router as user_router
from api.v1.endpoints.client_routes import router as client_router  
from api.v1.endpoints.role_routes import router as role_router


api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(user_router)
api_router.include_router(client_router)
api_router.include_router(role_router)