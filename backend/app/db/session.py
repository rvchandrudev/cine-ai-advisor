from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}"
    f"/{settings.postgres_db}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)