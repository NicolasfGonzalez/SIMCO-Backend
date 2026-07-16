from fastapi import FastAPI
from core.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            # Crear todas las tablas
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Conexión a la base de datos exitosa")
        print("✓ Tablas creadas correctamente")
    except Exception as e:
        print(f"⚠ Aviso: No se pudo conectar a la DB al iniciar: {e}")
        print("⚠ La app seguirá corriendo, pero necesitará conexión DB para funcionar")

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()