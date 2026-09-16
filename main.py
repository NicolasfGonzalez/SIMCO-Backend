from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models  # Carga todos los modelos mapeados en SQLAlchemy
from core.database import engine, Base
from api.v1.api import api_router
from api.v1.endpoints.auth_routes import router as auth_router
from core.database import engine, Base
from core.mongo import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Crear tablas en Postgres e inicializar MongoDB Atlas
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ PostgreSQL conectado correctamente")
    except Exception as e:
        print(f"✗ Error al conectar PostgreSQL: {e}")

    try:
        await connect_to_mongo()
    except Exception as e:
        print(f"✗ Error al conectar MongoDB Atlas: {e}")

    yield

    # 2. Shutdown: Liberar pools de conexiones
    await engine.dispose()
    await close_mongo_connection()
    print("✓ Conexiones cerradas correctamente")


app = FastAPI(
    title="SIMCO API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de Rutas
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Login"])


@app.get("/")
async def root():
    return {"message": "SIMCO API - Ver /docs para documentación"}