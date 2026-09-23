from fastapi import APIRouter
from api.v1.endpoints.user_routes import router as user_router
from api.v1.endpoints.client_routes import router as client_router  
from api.v1.endpoints.role_routes import router as role_router
from api.v1.endpoints.greenhouse_routes import router as greenhouse_router
from api.v1.endpoints.pile_routes import router as pile_router
from api.v1.endpoints.device_routes import router as device_router
from api.v1.endpoints.sensor_routes import router as sensor_router

api_router = APIRouter()

api_router.include_router(greenhouse_router)
api_router.include_router(user_router)
api_router.include_router(client_router)
api_router.include_router(role_router)
api_router.include_router(pile_router)
api_router.include_router(device_router)
api_router.include_router(sensor_router)