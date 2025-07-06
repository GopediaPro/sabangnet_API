from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from services.product.product_read_service import ProductReadService
from services.one_one_price.one_one_price_service import OneOnePriceService
from schemas.one_one_price.request.one_one_price_request import OneOnePriceCreate
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto, OneOnePriceBulkDto
from schemas.one_one_price.response.one_one_price_response import OneOnePriceBulkResponse


class ProductOneOnePriceUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.one_one_price_service = OneOnePriceService(session)
        self.product_read_service = ProductReadService(session)

    async def calculate_and_save_one_one_price(self, product_nm: str, gubun: str) -> OneOnePriceDto:
        product_raw_data_dto = await self.product_read_service.get_product_by_product_nm_and_gubun(product_nm=product_nm, gubun=gubun)

        # 상품 등록 데이터를 찾을 수 없는 경우 체크
        if product_raw_data_dto is None:
            raise ValueError(
                f"품번코드대량등록툴의 해당 데이터를 찾을 수 없습니다. (상품명: {product_nm}, 구분: {gubun})")

        test_product_raw_data_id, compayny_goods_cd, standard_price = \
            product_raw_data_dto.id, product_raw_data_dto.compayny_goods_cd, product_raw_data_dto.goods_price

        one_one_price_dto = await self.one_one_price_service.make_one_one_price_dto(
            test_product_raw_data_id=test_product_raw_data_id,
            compayny_goods_cd=compayny_goods_cd,
            product_nm=product_nm,
            standard_price=standard_price,
        )

        return await self.one_one_price_service.save_one_one_price_dto(one_one_price_dto)

    async def calculate_and_save_one_one_prices_bulk(self, product_nm_and_gubun_list: List[OneOnePriceCreate]) -> OneOnePriceBulkDto:
        success_count: int = 0
        error_count: int = 0 
        created_product_nm: List[int] = []
        errors: List[str] = []
        success_data: List[OneOnePriceDto] = []

        for product_nm_and_gubun in product_nm_and_gubun_list:
            product_nm, gubun = product_nm_and_gubun.product_nm, product_nm_and_gubun.gubun
            try:
                one_one_price_dto: OneOnePriceDto = await self.calculate_and_save_one_one_price(product_nm=product_nm, gubun=gubun)
                success_count += 1
                created_product_nm.append(one_one_price_dto.product_nm)
                success_data.append(one_one_price_dto)
            except Exception as e:
                errors.append(e)
                error_count += 1
                continue

        return OneOnePriceBulkDto(
            success_count=success_count,
            error_count=error_count,
            created_product_nm=created_product_nm,
            errors=errors,
            success_data=success_data,
        )