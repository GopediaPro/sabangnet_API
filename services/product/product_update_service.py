from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_repository import ProductRepository


class ProductUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repository = ProductRepository(session)

    async def update_product_id_by_compayny_goods_cd(self, compayny_goods_cd: str, product_id: int):
        await self.product_repository.update_product_id_by_compayny_goods_cd(compayny_goods_cd, product_id)
