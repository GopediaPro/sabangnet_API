from sqlalchemy.ext.asyncio import AsyncSession
from models.mall_price.mall_price import MallPrice
from sqlalchemy import insert

class MallPriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_mall_price(self, mall_price: MallPrice) -> MallPrice:
        self.session.add(mall_price)
        await self.session.flush()
        await self.session.commit()
        return mall_price