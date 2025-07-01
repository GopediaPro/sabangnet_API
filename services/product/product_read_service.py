from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_repository import ProductRepository
from models.product.product_raw_data import ProductRawData

class ProductReadService:
    def __init__(self, session: AsyncSession):
        self.product_repository = ProductRepository(session)

    async def get_product_by_compayny_goods_cd(self, compayny_goods_cd: str) -> ProductRawData:
        return await self.product_repository.find_product_raw_data_by_company_goods_cd(compayny_goods_cd)