import math
from decimal import Decimal
from utils.sabangnet_logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto
from repository.one_one_price_repository import OneOnePriceRepository


logger = get_logger(__name__)


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

    def __init__(self, session: AsyncSession):
        self.one_one_price_repository = OneOnePriceRepository(session)

    async def calculate_and_save_one_one_prices(
            self,
            test_product_raw_data_id: int,
            compayny_goods_cd: str,
            product_nm: str,
            standard_price: Decimal,
            ) -> OneOnePriceDto:
        """전체 프로세스 실행"""

        # 1. 어떤 제품의 기준 가격 조회
        if await self.one_one_price_repository.find_one_one_price_data_by_test_product_raw_data_id(test_product_raw_data_id) is not None:
            raise ValueError(f"상품명 {product_nm}에 대한 가격 정보가 이미 존재합니다. (test_product_raw_data_id: {test_product_raw_data_id})")

        # 2. 그 제품의 1+1 가격 계산
        one_one_price = self.calculate_one_one_price(standard_price)

        base_data = {
            'test_product_raw_data_id': test_product_raw_data_id,
            'compayny_goods_cd': compayny_goods_cd,
            'product_nm': product_nm,
            'standard_price': standard_price,
            'one_one_price': one_one_price,
        }

        # 3. 각 그룹별 가격 계산
        shop_prices = {}

        # 3-1. 그대로 적용 그룹
        for shop in self.SHOP_PRICE_MAPPING['group_same']:
            shop_prices[shop] = one_one_price

        # 3-2. +100 그룹
        shop_prices_plus_100 = self.calculate_shop_prices_plus_100(
            one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_plus100']:
            shop_prices[shop] = shop_prices_plus_100

        # 3-3. 105% 그룹
        shop_prices_105_percent = self.calculate_shop_prices_105_percent(
            one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_105']:
            shop_prices[shop] = shop_prices_105_percent

        # 3-4. 115% 그룹
        shop_prices_115_percent = self.calculate_shop_prices_115_percent(
            one_one_price)
        for shop in self.SHOP_PRICE_MAPPING['group_115']:
            shop_prices[shop] = shop_prices_115_percent

        # 4. DTO 생성
        one_one_price_dto = OneOnePriceDto(
            **base_data,
            **shop_prices
        )

        # 5. 저장
        created_model = await self.one_one_price_repository.create_one_one_price_data(one_one_price_dto)
        
        # 6. DB 모델을 DTO로 변환해서 반환
        return OneOnePriceDto.model_validate(created_model)

    def roundup_to_thousands(self, value: Decimal) -> Decimal:
        """천의 자리에서 올림 (roundup) - 엑셀 ROUNDUP과 동일한 동작"""
        # 엑셀의 ROUNDUP(value, -3)과 동일한 로직
        # 천의 자리에서 올림: 11800 -> 12000, 11801 -> 12000, 11999 -> 12000
        thousands = math.ceil(float(value) / 1000) * 1000
        return Decimal(str(thousands))
    
    def calculate_one_one_price(self, standard_price: Decimal) -> Decimal:
        """1+1 가격 계산"""
        # if(기준가 + 100 < 10000, roundup(기준가 * 2 + 2000, -3) - 100, roundup(기준가 * 2 + 1000, -3) - 100)
        if standard_price + 100 < 10000:
            base_price = standard_price * 2 + 2000
            rounded_price = self.roundup_to_thousands(base_price)
            return rounded_price - 100
        else:
            base_price = standard_price * 2 + 1000
            rounded_price = self.roundup_to_thousands(base_price)
            return rounded_price - 100

    def calculate_shop_prices_115_percent(self, one_one_price: Decimal) -> Decimal:
        """115% 적용 샵들 가격 계산"""
        # roundup(1+1가격 * 1.15, -3) - 100
        base_price = one_one_price * Decimal('1.15')
        rounded_price = self.roundup_to_thousands(base_price)
        return rounded_price - 100
        
    def calculate_shop_prices_105_percent(self, one_one_price: Decimal) -> Decimal:
        """105% 적용 샵들 가격 계산"""
        # roundup(1+1가격 * 1.05, -3) - 100
        base_price = one_one_price * Decimal('1.05')
        rounded_price = self.roundup_to_thousands(base_price)
        return rounded_price - 100
        
    def calculate_shop_prices_plus_100(self, one_one_price: Decimal) -> Decimal:
        """1+1가격 + 100 적용 샵들"""
        # 1+1가격 + 100
        return one_one_price + 100