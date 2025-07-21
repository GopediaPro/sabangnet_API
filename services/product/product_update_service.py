from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_repository import ProductRepository
from schemas.product.modified_product_dto import ModifiedProductDataDto


class ProductUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repository = ProductRepository(session)

    async def update_product_id_by_compayny_goods_cd(self, compayny_goods_cd: str, product_id: int):
        await self.product_repository.update_product_id_by_compayny_goods_cd(compayny_goods_cd, product_id)

    async def modify_product_name(self, compayny_goods_cd: str, product_name: str) -> ModifiedProductDataDto:
        product_raw_data = await self.product_repository.find_product_raw_data_by_company_goods_cd(compayny_goods_cd)
        if product_raw_data is None:
            raise ValueError(f"Product raw data not found: {compayny_goods_cd}")
        
        modified_product_data = await self.product_repository.\
            find_modified_product_data_by_product_raw_data_id(product_raw_data.id)
        
        rev = 0 if modified_product_data is None else modified_product_data.rev + 1
        
        result = await self.product_repository.save_modified_product_name(
            product_raw_data=product_raw_data, rev=rev, product_name=product_name)
        
        dto = ModifiedProductDataDto.model_validate(result)
        return dto
