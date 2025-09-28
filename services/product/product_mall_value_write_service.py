from sqlalchemy.ext.asyncio import AsyncSession
from models.mall_price.product_mall_value import ProductMallValue
from schemas.mall_price.product_mall_value_dto import ProductMallValueDto
from repository.product_mall_value_repository import ProductMallValueRepository


class ProductMallValueWriteService:
    def __init__(self, session: AsyncSession):
        self.product_mall_value_repository = ProductMallValueRepository(session)

    async def setting_product_mall_value(self, product_raw_data_id: int, 
                                       standard_price: int, product_nm: str, 
                                       compayny_goods_cd: str, gubun: str, **kwargs) -> ProductMallValueDto:
        """ProductMallValue 설정 및 upsert"""
        new_obj = ProductMallValue.builder(
            product_raw_data_id=product_raw_data_id,
            standard_price=standard_price,
            product_nm=product_nm,
            compayny_goods_cd=compayny_goods_cd,
            gubun=gubun,
            **kwargs
        )
        
        # upsert 수행
        product_mall_value = await self.product_mall_value_repository.upsert_product_mall_value(new_obj)
        
        return ProductMallValueDto.model_validate(product_mall_value)
