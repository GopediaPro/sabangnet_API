from typing import List
from decimal import Decimal
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from models.one_one_price.one_one_price import OneOnePrice
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto


class OneOnePriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_one_one_price_data(self, data: OneOnePriceDto) -> OneOnePrice:
        """쇼핑몰별 1+1 가격 데이터 생성"""
        try:
            data_dict = data.model_dump(exclude_none=True)
            query = insert(OneOnePrice).values(**data_dict).returning(OneOnePrice)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
    
    # async def bulk_create_one_one_price_data(self, data_list: List[OneOnePriceDto]) -> List[int]:
    #     """쇼핑몰별 1+1 가격 데이터 대량 생성"""
    #     try:
    #         data_dict_list = [data.model_dump(exclude_none=True) for data in data_list]
    #         query = insert(OneOnePrice).values(data_dict_list).returning(OneOnePrice.id)
    #         result = await self.session.execute(query)
    #         created_ids = [row[0] for row in result.fetchall()]
    #         await self.session.commit()
    #         return created_ids
    #     except Exception as e:
    #         await self.session.rollback()
    #         raise e
    
    async def find_all_one_one_price_data(self) -> List[OneOnePrice]:
        """쇼핑몰별 1+1 가격 데이터 전체 조회"""
        try:
            query = select(OneOnePrice).order_by(OneOnePrice.id)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def find_one_one_price_data_by_test_product_raw_data_id(self, test_product_raw_data_id: int) -> OneOnePrice:
        """test_product_raw_data_id로 쇼핑몰별 가격 데이터 조회"""
        try:
            query = select(OneOnePrice).where(OneOnePrice.test_product_raw_data_id == test_product_raw_data_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
    
    async def find_one_one_price_data_by_product_nm(self, product_nm: str) -> OneOnePrice:
        """product_nm으로 쇼핑몰별 가격 데이터 조회"""
        try:
            query = select(OneOnePrice).where(OneOnePrice.product_nm == product_nm)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()