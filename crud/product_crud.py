from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData
from pathlib import Path


class ProductCRUD:

    # 데이터베이스에 insert -> id 리스트 반환
    async def product_raw_data_create(self, product_data: list[dict]) -> list[int]:
        async for session in get_async_session():
            query = insert(ProductRawData).returning(ProductRawData.id)
            result = await session.execute(query, product_data)
            await session.commit()
            return [row[0] for row in result.fetchall()]

    async def prodout_prop1_cd_update(self, product_raw_id: int, prop1_cd: str = "035") -> str:
        # 빈값인 경우 기본값 사용
        if not prop1_cd:
            prop1_cd = "035"

        async for session in get_async_session():
            # 1. raw 데이터 조회
            result = await session.execute(
                select(ProductRawData).where(
                    ProductRawData.id == product_raw_id)
            )
            raw_product = result.scalar_one_or_none()

            if raw_product is None:
                print(f"ID {product_raw_id}에 해당하는 상품을 찾을 수 없습니다.")
                return None

            print(f"변경전 prop1_cd: {raw_product.prop1_cd}")
            # 2. 속성값 prop1_cd 수정
            raw_product.prop1_cd = prop1_cd
            print(f"변경후 prop1_cd: {raw_product.prop1_cd}")

            # 3. ModifiedProductData에 insert
            new_raw_dict = raw_product.__dict__.copy()
            new_raw_dict.pop('_sa_instance_state')  # SQLAlchemy 내부 속성 제거
            new_raw_dict.pop('id')  # Primary Key 제거 (자동 생성)
            new_raw_dict['product_raw_data_id'] = raw_product.id  # 외래키 설정

            query = insert(ModifiedProductData).returning(
                ModifiedProductData.prop1_cd)
            result = await session.execute(query, new_raw_dict)
            await session.commit()

            return result.scalar()
