from sqlalchemy.ext.asyncio import AsyncSession
from models.mall_price.mall_price import MallPrice
from schemas.mall_price.mall_price_dto import MallPriceDto
from repository.mall_price_repository import MallPriceRepository


class MallPriceWriteService:
    def __init__(self, session: AsyncSession):
        self.mall_price_repository = MallPriceRepository(session)

    async def setting_mall_price(self, product_raw_data_id: int, 
                                 standard_price: int, product_nm: str, compayny_goods_cd: str) -> MallPriceDto:
        new_obj = MallPrice.builder(
            product_raw_data_id=product_raw_data_id,
            standard_price=standard_price,
            product_nm=product_nm,
            compayny_goods_cd=compayny_goods_cd
        )
        if await self.mall_price_repository.exist_mall_price_by_product_raw_data_id(product_raw_data_id=product_raw_data_id):
            mall_price = await self.mall_price_repository.update_mall_price_by_product_raw_data_id(
                product_raw_data_id=product_raw_data_id,
                new_obj=new_obj
            )
        else:
            mall_price = await self.mall_price_repository.save_mall_price(new_obj)
        return MallPriceDto.model_validate(mall_price)