import asyncpg
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class DBSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_sslmode: Optional[str] = "disable"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = DBSettings()

DB_DSN = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}?sslmode={settings.db_sslmode}"

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
