from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import engine, Base
from api.v1.api import api_router

#  Crear     la app
app = FastAPI(
    title="SIMCO API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

#  CORS
origins = [
    "http://localhost:5173",  # frontend React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # o ["*"] en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#   routers
app.include_router(api_router, prefix="/api/v1")

#  Eventos
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ BD conectada correctamente")
    except Exception:
        pass

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

#  Ruta base
@app.get("/")
async def root():
    return {"message": "SIMCO API - Ver /docs para documentación"}