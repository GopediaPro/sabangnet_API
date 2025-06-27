import asyncpg
from typing import Optional
from core.settings import SETTINGS
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_DSN = f"postgresql://{SETTINGS.DB_USER}:{SETTINGS.DB_PASSWORD}@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_NAME}?sslmode={SETTINGS.DB_SSLMODE}"

_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=DB_DSN)
    return _pool

async def close_db_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

DATABASE_URL = f"postgresql+asyncpg://{SETTINGS.DB_USER}:{SETTINGS.DB_PASSWORD}@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_NAME}"

# 비동기 엔진 생성
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  
    future=True,
    pool_pre_ping=True, 
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        return session

async def test_db_write(value: str) -> bool:
    pool = await get_db_pool()
    table = SETTINGS.DB_TEST_TABLE
    column = SETTINGS.DB_TEST_COLUMN
    query = f'INSERT INTO "{table}" ("{column}") VALUES ($1) RETURNING "{column}"'
    async with pool.acquire() as conn:
        result = await conn.fetchval(query, value)
        return result == value