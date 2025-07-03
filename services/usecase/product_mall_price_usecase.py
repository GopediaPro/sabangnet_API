from sqlalchemy.ext.asyncio import AsyncSession
from services.mall_price.mall_price_write_service import MallPriceWriteService
from services.product_registration.product_registration_read_service import ProductRegistrationReadService
from schemas.mall_price.mall_price_dto import MallPriceDto

class ProductMallPriceUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mall_price_write_service = MallPriceWriteService(session)
        self.product_registration_read_service = ProductRegistrationReadService(session)

    async def setting_mall_price(self, product_nm: str) -> MallPriceDto:
        product_registration_raw_data = await self.product_registration_read_service.\
            get_product_registration_by_product_nm(product_nm=product_nm)
        if product_registration_raw_data is None:
            raise ValueError(f"Product raw data not found: {product_nm}")
        
        mall_price_dto = await self.mall_price_write_service.\
            setting_mall_price(product_registration_raw_data_id=product_registration_raw_data.id,
                               standard_price=product_registration_raw_data.goods_price,
                               product_nm=product_nm)
        return mall_price_dto

    