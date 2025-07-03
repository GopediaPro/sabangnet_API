from sqlalchemy.ext.asyncio import AsyncSession
from schemas.mall_price.mall_price_dto import MallPriceDto
from repository.mall_price_repository import MallPriceRepository
from models.mall_price.mall_price import MallPrice

class MallPriceWriteService:
    def __init__(self, session: AsyncSession):
        self.mall_price_repository = MallPriceRepository(session)

    async def setting_mall_price(self, product_registration_raw_data_id: int, 
                                 standard_price: int, product_nm: str) -> MallPriceDto:
        if await self.mall_price_repository.exist_mall_price_by_product_registration_raw_data_id(product_registration_raw_data_id):
            raise ValueError(f"Mall price already exists: {product_registration_raw_data_id}")

        mall_price = MallPrice.builder(product_registration_raw_data_id=product_registration_raw_data_id,
                                        standard_price=standard_price,
                                          product_nm=product_nm)
        
        return MallPriceDto.model_validate(await self.mall_price_repository.save_mall_price(mall_price))