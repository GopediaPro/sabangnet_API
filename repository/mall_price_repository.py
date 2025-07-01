from sqlalchemy.ext.asyncio import AsyncSession
from models.mall_price.mall_price import MallPrice
from sqlalchemy import select

class MallPriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_mall_price(self, mall_price: MallPrice) -> MallPrice:
        self.session.add(mall_price)
        await self.session.flush()
        await self.session.commit()
        return mall_price
    
    async def exist_mall_price_by_product_registration_raw_data_id(self, product_registration_raw_data_id: int) -> bool:
        result = await self.session.execute(
            select(MallPrice).where(MallPrice.product_registration_raw_data_id == product_registration_raw_data_id)
        )
        return result.scalar_one_or_none() is not None