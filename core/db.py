from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from core.configs import database_settings

DATABASE_URL = (
    f"postgresql+asyncpg://{database_settings.POSTGRES_USER}:"
    f"{database_settings.POSTGRES_PASSWORD}@"
    f"{database_settings.POSTGRES_HOST}:{database_settings.POSTGRES_PORT}/"
    f"{database_settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise





