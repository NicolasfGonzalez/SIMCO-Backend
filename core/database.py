from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Engine async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Cambiar a True para debugging
    future=True,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_size=20,
    max_overflow=0
)

# Sesión async - Configuración correcta
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Base para modelos
Base = declarative_base()

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()