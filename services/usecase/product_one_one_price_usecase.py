from sqlalchemy.ext.asyncio import AsyncSession
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto
from services.one_one_price.one_one_price_service import OneOnePriceService
from services.product_registration.product_registration_read_service import ProductRegistrationReadService


class ProductOneOnePriceUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.one_one_price_service = OneOnePriceService(session)
        self.product_registration_read_service = ProductRegistrationReadService(session)

    async def calculate_and_save_one_one_prices(self, products_nm: str) -> OneOnePriceDto:
        product_registration_raw_data_id_and_price = await self.product_registration_read_service.\
            get_product_id_and_price_by_products_nm(products_nm=products_nm)
        
        # 상품 등록 데이터를 찾을 수 없는 경우 체크
        if product_registration_raw_data_id_and_price is None:
            raise ValueError(f"상품 등록 데이터를 찾을 수 없습니다. (상품명: {products_nm})")

        product_registration_raw_data_id, standard_price = product_registration_raw_data_id_and_price

        return await self.one_one_price_service.calculate_and_save_one_one_prices(
            product_registration_raw_data_id=product_registration_raw_data_id,
            product_nm=products_nm,
            standard_price=standard_price,
        )
