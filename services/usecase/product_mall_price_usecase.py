from sqlalchemy.ext.asyncio import AsyncSession
from services.mall_price.mall_price_write_service import MallPriceWriteService
from services.product.product_read_service import ProductReadService
from schemas.mall_price.mall_price_dto import MallPriceDto

class ProductMallPriceUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mall_price_write_service = MallPriceWriteService(session)
        self.product_read_service = ProductReadService(session)

    async def setting_mall_price(self, gubun: str, product_nm: str) -> MallPriceDto:
        product_raw_data_dto = await self.product_read_service.\
            get_product_by_product_nm_and_gubun(product_nm=product_nm, gubun=gubun)
        
        mall_price_dto = await self.mall_price_write_service.\
            setting_mall_price(product_raw_data_id=product_raw_data_dto.id,
                               standard_price=product_raw_data_dto.goods_price,
                               product_nm=product_nm,
                               compayny_goods_cd=product_raw_data_dto.compayny_goods_cd)
        return mall_price_dto

    