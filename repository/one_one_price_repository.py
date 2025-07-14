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

    async def find_all_one_one_price_data(self) -> list[OneOnePrice]:
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

    async def update_one_one_price_data(self, data: OneOnePriceDto) -> OneOnePrice:
        """쇼핑몰별 1+1 가격 데이터 수정"""
        try:
            one_one_price_data = await self.find_one_one_price_data_by_test_product_raw_data_id(data.test_product_raw_data_id)
            if one_one_price_data is None:
                raise ValueError(f"OneOnePrice data not found: {data.test_product_raw_data_id}")
            for field in OneOnePrice.__table__.columns.keys():
                if field == "id":
                    continue
                setattr(one_one_price_data, field, getattr(data, field))
            await self.session.commit()
            return one_one_price_data
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()