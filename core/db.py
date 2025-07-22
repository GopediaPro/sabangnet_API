import asyncpg
from typing import Optional
from core.settings import SETTINGS
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

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
    echo=False,  
    future=True,
    pool_pre_ping=True, 
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def test_db_write(value: str) -> bool:
    pool = await get_db_pool()
    table = SETTINGS.DB_TEST_TABLE
    column = SETTINGS.DB_TEST_COLUMN
    query = f'INSERT INTO "{table}" ("{column}") VALUES ($1) RETURNING "{column}"'
    async with pool.acquire() as conn:
        result = await conn.fetchval(query, value)
        return result == value

async def create_tables():
    """
    데이터베이스 테이블 생성 (폴더 이름 순서로 정렬)
    """
    try:
        from models.base_model import Base
        from models.certification_detail.certification_detail import CertificationDetail
        from models.count_executing_data.count_executing_data import CountExecuting
        from models.down_form_orders.down_form_order import BaseDownFormOrder
        from models.macro.macro_info import MacroInfo
        from models.mall_certification_handling.mall_certification_handling import MallCertificationHandling
        from models.mall_price.mall_price import MallPrice
        from models.one_one_price.one_one_price import OneOnePrice
        from models.product.modified_product_data import ModifiedProductData
        from models.product.product_mycategory_data import ProductMycategoryData
        from models.product.product_raw_data import ProductRawData
        from models.product.product_registration_data import ProductRegistrationRawData
        from models.receive_orders.receive_orders import ReceiveOrders
        from models.batch_process import BatchProcess
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("데이터베이스 테이블 생성 완료!")
        
    except Exception as e:
        logger.error(f"테이블 생성 중 오류 발생: {e}")
        raise