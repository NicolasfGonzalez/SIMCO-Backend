from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings

# Engine async (ARREGLADO)
engine = create_async_engine(
    settings.async_database_url, 
    echo=False,
    future=True,
    pool_pre_ping=True,

    connect_args={
        "statement_cache_size": 0
    },

    poolclass=NullPool
)

# Sesión async
AsyncSessionLocal = sessionmaker(
    bind=engine,
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
        yield session