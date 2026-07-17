from fastapi import FastAPI
from core.database import engine, Base
from api.v1.api import api_router

app = FastAPI(title="SIMCO API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ BD conectada correctamente")
    except Exception:
        pass  # Silenciosamente si falla (network issue, etc)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

@app.get("/")
async def root():
    return {"message": "SIMCO API - Ver /docs para documentación"}