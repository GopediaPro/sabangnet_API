import asyncpg
import os
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SSLMODE = os.getenv('DB_SSLMODE', 'disable')

DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSLMODE}"

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


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 비동기 엔진 생성
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로그 출력
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 세션 의존성 함수
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()