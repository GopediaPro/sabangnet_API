from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from models.product.product_raw_data import ProductRawData

from pathlib import Path

class ProductCRUD:

    # 데이터베이스에 insert -> id 리스트 반환
    async def product_raw_data_create(self, product_data: list[dict]) -> list[int]:
        async for session in get_async_session():
            query = insert(ProductRawData).returning(ProductRawData.id)
            result = await session.execute(query, product_data)
            await session.commit()
            return [row[0] for row in result.fetchall()]
    

