from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData
from models.product.test_product_raw_data import TestProductRawData


class ProductRepository:
    def __init__(self, session: AsyncSession = None):
        self.session = session


    async def product_raw_data_create(self, product_data: list[dict]) -> list[int]:
        """
        Insert data to database and return id list.
        """
        try:
            query = insert(TestProductRawData).returning(TestProductRawData.id)
            result = await self.session.execute(query, product_data)
            await self.session.commit()
            return [row[0] for row in result.fetchall()]
        except IntegrityError as e:
            await self.session.rollback()
            print(f"[IntegrityError] {e}")
            raise
        except Exception as e:
            await self.session.rollback()
            print(f"[Unknown Error] {e}")
            raise
        finally:
            await self.session.close()

    async def product_get_next_rev(self, product_raw_id: int) -> int:
        """
        Get next rev.
        """
        session = await self.get_session()
        query = select(func.max(ModifiedProductData.rev)).where(
            ModifiedProductData.product_raw_data_id == product_raw_id)
        result = await session.execute(query)
        max_rev = result.scalar_one_or_none()

        return (max_rev or 0) + 1

    async def prodout_prop1_cd_update(self, product_raw_id: int, prop1_cd: str = "035") -> str:
        """
        Update prop1_cd value.
        """
        # 빈값인 경우 기본값 사용
        if not prop1_cd:
            prop1_cd = "035"

        # 1. raw 데이터 조회
        result = await self.session.execute(
            select(ProductRawData).where(
                ProductRawData.id == product_raw_id)
        )
        raw_data = result.scalar_one_or_none()

        if raw_data is None:
            print(f"ID {product_raw_id}에 해당하는 상품을 찾을 수 없습니다.")
            return None

        # 2. 다음 rev 조회
        next_rev = await self.product_get_next_rev(self.session, raw_data.id)

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
        result = await self.session.execute(query, new_raw_dict)
        await self.session.commit()

        return result.scalar()

    async def get_unmodified_raws(self) -> list[dict]:
        """
        Get unmodified product data.
        """
        query = (
            select(ProductRawData)
            .outerjoin(ModifiedProductData, ProductRawData.id == ModifiedProductData.product_raw_data_id)
            .where(ModifiedProductData.product_raw_data_id == None)
        )
        result = await self.session.execute(query)
        raw_data: list[dict] = [row.__dict__ for row in result.scalars().all()]
        return raw_data

    async def get_modified_raws(self) -> list[dict]:
        """
        Get modified product data.
        """
        query = (
            select(ModifiedProductData)
            .distinct(ModifiedProductData.product_raw_data_id)
            .order_by(ModifiedProductData.product_raw_data_id, ModifiedProductData.rev.desc())
        )
        result = await self.session.execute(query)
        raw_data: list[dict] = [row.__dict__ for row in result.scalars().all()]
        return raw_data
    
    async def modify_goods_name(self, product_raw_id: int, goods_nm: str) -> ModifiedProductData:
        
        return await self.session.update(ModifiedProductData, product_raw_id, goods_nm=goods_nm)
