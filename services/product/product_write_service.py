from schemas.product.modified_product_dto import ModifiedProductDataDto
from schemas.product.response.product_response import ProductNameResponse
from repository.product_repository import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ProductWriteService:
    def __init__(self, session: AsyncSession) -> None:
        self.product_repository = ProductRepository(session)

    async def modify_product_name(self, compayny_goods_cd: str, product_name: str) -> ModifiedProductDataDto:
        result = await self.product_repository.\
            save_modified_product_name(compayny_goods_cd=compayny_goods_cd, product_name=product_name)
        
        dto = ModifiedProductDataDto.model_validate(result)

        return dto
    