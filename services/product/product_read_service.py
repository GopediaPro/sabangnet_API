from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_repository import ProductRepository
from models.product.product_raw_data import ProductRawData
from schemas.product.product_raw_data_dto import ProductRawDataDto

class ProductReadService:
    def __init__(self, session: AsyncSession):
        self.product_repository = ProductRepository(session)

    async def get_product_by_compayny_goods_cd(self, compayny_goods_cd: str) -> ProductRawData:
        return await self.product_repository.find_product_raw_data_by_company_goods_cd(compayny_goods_cd)
    
    async def get_product_by_product_nm_and_gubun(self, product_nm: str, gubun: str) -> ProductRawDataDto:
        res = await self.product_repository.find_product_raw_data_by_product_nm_and_gubun(product_nm, gubun)
        if res is None:
            raise ValueError(f"Product raw data not found: {product_nm}")
        return ProductRawDataDto.model_validate(res)
    
    async def get_product_raw_data_all(self) -> list[ProductRawDataDto]:
        objects = await self.product_repository.get_product_raw_data_all()
        return [ProductRawDataDto.model_validate(obj) for obj in objects]