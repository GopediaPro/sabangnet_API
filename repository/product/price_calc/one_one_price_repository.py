from sqlalchemy.ext.asyncio import AsyncSession
from schemas.product.price_calc.one_one_price_dto import OneOneDto
from models.product.price_calc.one_one_price_data import OneOnePriceData
from sqlalchemy import select, insert
from typing import List
from decimal import Decimal


class OneOnePriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_one_one_price_data(self, data: OneOneDto) -> OneOnePriceData:
        """쇼핑몰별 1+1 가격 데이터 생성"""
        try:
            data_dict = data.model_dump(exclude_none=True)
            query = insert(OneOnePriceData).values(**data_dict).returning(OneOnePriceData)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def bulk_create_one_one_price_data(self, data_list: List[OneOneDto]) -> List[int]:
        """쇼핑몰별 1+1 가격 데이터 대량 생성"""
        try:
            data_dict_list = [data.model_dump(exclude_none=True) for data in data_list]
            query = insert(OneOnePriceData).values(data_dict_list).returning(OneOnePriceData.id)
            result = await self.session.execute(query)
            created_ids = [row[0] for row in result.fetchall()]
            await self.session.commit()
            return created_ids
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def find_all_one_one_price_data(self) -> List[OneOnePriceData]:
        """쇼핑몰별 1+1 가격 데이터 전체 조회"""
        query = select(OneOnePriceData).order_by(OneOnePriceData.test_product_raw_data_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_one_one_price_data_by_standard_price(self, standard_price: Decimal) -> OneOnePriceData:
        """기준 가격으로 쇼핑몰별 가격 데이터 조회"""
        query = select(OneOnePriceData).where(OneOnePriceData.standard_price == standard_price)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_one_one_price_data_by_one_one_price(self, one_one_price: Decimal) -> OneOnePriceData:
        """1+1 가격으로 쇼핑몰별 가격 데이터 조회"""
        query = select(OneOnePriceData).where(OneOnePriceData.one_one_price == one_one_price)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_one_one_price_data_by_test_product_raw_data_id(self, test_product_raw_data_id: int) -> OneOnePriceData:
        """test_product_raw_data_id로 쇼핑몰별 가격 데이터 조회"""
        query = select(OneOnePriceData).where(OneOnePriceData.test_product_raw_data_id == test_product_raw_data_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()