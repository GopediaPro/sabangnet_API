from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func

from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData
from pathlib import Path


class ProductRawDataCRUD:

    # 데이터베이스에 insert -> id 리스트 반환
    async def product_raw_data_create(self, product_data: list[dict]) -> list[int]:
        async for session in get_async_session():
            query = insert(ProductRawData).returning(ProductRawData.id)
            result = await session.execute(query, product_data)
            await session.commit()
            return [row[0] for row in result.fetchall()]

    async def product_get_next_rev(self, session: AsyncSession, product_raw_id: int) -> int:
        async for session in get_async_session():
            query = select(func.max(ModifiedProductData.rev)).where(
                ModifiedProductData.product_raw_data_id == product_raw_id)
            result = await session.execute(query)
            max_rev = result.scalar_one_or_none()
            print('*'*100)
            print(max_rev or 0)
            return (max_rev or 0) + 1

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
            raw_data = result.scalar_one_or_none()

            if raw_data is None:
                print(f"ID {product_raw_id}에 해당하는 상품을 찾을 수 없습니다.")
                return None

            # 2. 다음 rev 조회
            next_rev = await self.product_get_next_rev(session, raw_data.id)

            # 3. 속성값 제거
            new_raw_dict = raw_data.__dict__.copy()
            new_raw_dict.pop('_sa_instance_state')
            new_raw_dict.pop('id')
            new_raw_dict.pop('created_at')
            new_raw_dict.pop('updated_at')

            # 4. 속성값 변경
            print(f"변경전 prop1_cd: {new_raw_dict['prop1_cd']}")
            new_raw_dict["prop1_cd"] = prop1_cd
            new_raw_dict['product_raw_data_id'] = raw_data.id  # 외래키 설정
            new_raw_dict['rev'] = next_rev  # 다음 rev 설정
            print(f"변경후 prop1_cd: {new_raw_dict['prop1_cd']}")
            print(new_raw_dict)

            # 5. ModifiedProductData에 insert
            query = insert(ModifiedProductData).returning(
                ModifiedProductData.prop1_cd)
            result = await session.execute(query, new_raw_dict)
            await session.commit()

            return result.scalar()

