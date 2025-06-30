from sqlalchemy.ext.asyncio import AsyncSession
from repository.product.price_calc.one_one_price_repository import OneOnePriceRepository
from repository.product_registration_repository import ProductRegistrationRepository
from repository.product_repository import ProductRepository
from utils.product.price_calculator import PriceCalculator
from models.product.price_calc.one_one_price_data import OneOnePriceData
from schemas.product.price_calc.one_one_price_dto import OneOneDto
from decimal import Decimal


class OneOnePriceService:

    """1+1 가격 계산 서비스"""

    SHOP_PRICE_MAPPING = {
        # 115%
        'group_115': ('shop0007', 'shop0042', 'shop0087', 'shop0094', 'shop0121', 'shop0129', 'shop0154', 'shop0650'),

        # 105%
        'group_105': ('shop0029', 'shop0189', 'shop0322', 'shop0444', 'shop0100', 'shop0298', 'shop0372'),

        # 1+1가격 그대로 적용
        'group_same': ('shop0381', 'shop0416', 'shop0449', 'shop0498', 'shop0583', 'shop0587', 'shop0661', 'shop0075', 'shop0319', 'shop0365', 'shop0387'),

        # 1+1가격 + 100
        'group_plus100': ('shop0055', 'shop0067', 'shop0068', 'shop0273', 'shop0464')
    }

    def __init__(
        self,
        session: AsyncSession,
        product_registration_repository: ProductRegistrationRepository,
        product_repository: ProductRepository,
        one_one_price_repository: OneOnePriceRepository,
    ):
        self.session = session
        self.product_registration_repository = product_registration_repository
        self.product_repository = product_repository
        self.one_one_price_repository = one_one_price_repository

    async def calculate_and_save_one_one_prices(self, model_nm: str) -> OneOnePriceData:
        """전체 프로세스 실행"""
        # 1. 어떤 제품의 기준 가격 조회
        standard_price = await self.product_registration_repository.get_product_price_by_products_nm(model_nm)
        
        # 상품명에 대한 가격 정보를 찾을 수 없는 경우 체크
        if standard_price is None:
            raise ValueError(f"상품명 {model_nm}에 대한 가격 정보를 찾을 수 없습니다.")

        # 2. 그 제품의 FK 조회
        fk_id = await self.product_repository.find_product_raw_data_by_model_nm_and_mall_gubun(model_nm, "1+1")
        
        # 상품명을 찾을 수 없는 경우 체크
        if fk_id is None:
            raise ValueError(f"상품명 {model_nm}을 찾을 수 없습니다.")

        # 3-1. 그 제품의 1+1 가격 계산
        one_one_price = PriceCalculator.calculate_one_one_price(standard_price)

        # 3-2 각 그룹별 가격 계산
        shop_prices = {}

        # 그대로 적용 그룹
        for shop in self.SHOP_PRICE_MAPPING['group_same']:
            shop_prices[shop] = one_one_price

        # +100 그룹
        shop_prices_plus_100 = PriceCalculator.calculate_shop_prices_plus_100(one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_plus100']:
            shop_prices[shop] = shop_prices_plus_100

        # 105% 그룹
        shop_prices_105_percent = PriceCalculator.calculate_shop_prices_105_percent(one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_105']:
            shop_prices[shop] = shop_prices_105_percent

        # 115% 그룹
        shop_prices_115_percent = PriceCalculator.calculate_shop_prices_115_percent(one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_115']:
            shop_prices[shop] = shop_prices_115_percent
            
        # 4. DTO 생성
        one_one_dto = OneOneDto(
            test_product_raw_data_id=fk_id,
            standard_price=standard_price,
            one_one_price=one_one_price,
            **shop_prices
        )

        # 5. 저장
        return await self.one_one_price_repository.create_one_one_price_data(one_one_dto)
