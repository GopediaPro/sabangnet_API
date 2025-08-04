import math
import pytest
from decimal import Decimal
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto
from services.one_one_price.one_one_price_service import OneOnePriceService
from api.v1.endpoints.one_one_price import get_product_one_one_price_usecase
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase


@pytest.fixture
def mock_product_one_one_price_usecase(test_app):
    """ProductOneOnePriceUsecase 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_usecase = AsyncMock(spec=ProductOneOnePriceUsecase)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_usecase
    
    yield mock_usecase
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_product_one_one_price_service(test_app):
    """OneOnePriceCalculator 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=OneOnePriceService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_one_one_price_usecase] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_one_one_price_list():
    """테스트용 1+1 가격 정보 목록"""
    return MOCK_TABLES["one_one_price"]


@pytest.fixture
def sample_one_one_price_request_data():
    """
    테스트용 상품 요청 데이터
    mock test product raw data 에서는 마스터, 전문몰, 1+1 선택을 [i % 3] 으로 정하기 때문에,
    테스트상품'2'부터 시작함.
    """

    mock_product2 = MOCK_TABLES["product_raw_data"][2]
    
    return {
        "product_nm": mock_product2["product_nm"],
        "gubun": mock_product2["gubun"]
    }


@pytest.fixture
def sample_one_one_price_bulk_request_data():
    """테스트용 상품 요청 데이터"""

    mock_product2 = MOCK_TABLES["product_raw_data"][2]
    mock_product5 = MOCK_TABLES["product_raw_data"][5]

    return {
        "product_nm_and_gubun_list": [
            {
                "product_nm": mock_product2["product_nm"],
                "gubun": mock_product2["gubun"]
            },
            {
                "product_nm": mock_product5["product_nm"],
                "gubun": mock_product5["gubun"]
            }
        ]
    }


@pytest.fixture
def sample_one_one_price_bulk_request_data_partial_success():
    """테스트용 상품 요청 데이터 부분적 성공 테스트"""

    mock_product2 = MOCK_TABLES["product_raw_data"][2]
    mock_product5 = MOCK_TABLES["product_raw_data"][5]

    return {
        "product_nm_and_gubun_list": [
            {
                "product_nm": mock_product2["product_nm"],
                "gubun": mock_product2["gubun"]
            },
            {
                "product_nm": mock_product5["product_nm"],
                "gubun": mock_product5["gubun"]
            },
            {
                "product_nm": "잘못된 상품",
                "gubun": "잘못된 구분"
            }
        ]
    }


@pytest.fixture
def expected_one_one_price_dto_from_second_data():
    """Mock table 두 번째 데이터로부터 생성된 예상 응답"""
    
    i = 2
    mock_product = MOCK_TABLES["product_raw_data"][i]  # 2번째 상품 데이터
    goods_price = mock_product["goods_price"]

    # 1+1 가격 계산
    if goods_price + 100 < 10000:
        base_price = goods_price * 2 + 2000
        rounded_price = math.ceil(float(base_price) / 1000) * 1000
        one_one_price = Decimal(str(rounded_price - 100))
    else:
        base_price = goods_price * 2 + 1000
        rounded_price = math.ceil(float(base_price) / 1000) * 1000
        one_one_price = Decimal(str(rounded_price - 100))
    
    # 115% 적용 샵들 가격 계산
    base_price_115 = one_one_price * Decimal('1.15')
    rounded_price_115 = math.ceil(float(base_price_115) / 1000) * 1000
    one_one_price_115 = Decimal(str(rounded_price_115 - 100))
    
    # 105% 적용 샵들 가격 계산
    base_price_105 = one_one_price * Decimal('1.05')
    rounded_price_105 = math.ceil(float(base_price_105) / 1000) * 1000
    one_one_price_105 = Decimal(str(rounded_price_105 - 100))
    
    # 1+1가격 + 100 적용 샵들
    one_one_price_p100 = one_one_price + 100
    
    return OneOnePriceDto(
        test_product_raw_data_id=i,
        product_nm=mock_product["product_nm"],
        compayny_goods_cd=mock_product["compayny_goods_cd"],
        standard_price=Decimal(str(goods_price)),
        one_one_price=one_one_price,
        shop0007=one_one_price_115,  # group_115
        shop0042=one_one_price_115,  # group_115
        shop0087=one_one_price_115,  # group_115
        shop0094=one_one_price_115,  # group_115
        shop0121=one_one_price_115,  # group_115
        shop0129=one_one_price_115,  # group_115
        shop0154=one_one_price_115,  # group_115
        shop0650=one_one_price_115,  # group_115
        shop0029=one_one_price_105,  # group_105
        shop0189=one_one_price_105,  # group_105
        shop0322=one_one_price_105,  # group_105
        shop0444=one_one_price_105,  # group_105
        shop0100=one_one_price_105,  # group_105
        shop0298=one_one_price_105,  # group_105
        shop0372=one_one_price_105,  # group_105
        shop0381=one_one_price,      # group_same
        shop0416=one_one_price,      # group_same
        shop0449=one_one_price,      # group_same
        shop0498=one_one_price,      # group_same
        shop0583=one_one_price,      # group_same
        shop0587=one_one_price,      # group_same
        shop0661=one_one_price,      # group_same
        shop0075=one_one_price,      # group_same
        shop0319=one_one_price,      # group_same
        shop0365=one_one_price,      # group_same
        shop0387=one_one_price,      # group_same
        shop0055=one_one_price_p100, # group_plus100
        shop0067=one_one_price_p100, # group_plus100
        shop0068=one_one_price_p100, # group_plus100
        shop0273=one_one_price_p100, # group_plus100
        shop0464=one_one_price_p100  # group_plus100
    )


@pytest.fixture
def invalid_product_request_data():
    """존재하지 않는 상품 요청 데이터"""
    return {
        "product_nm": "존재하지않는상품",
        "gubun": "1+1"
    }


@pytest.fixture
def empty_fields_request_data():
    """빈 필드 요청 데이터"""
    return {
        "product_nm": "",
        "gubun": ""
    }


@pytest.fixture
def missing_gubun_request_data():
    """gubun 필드가 누락된 요청 데이터"""
    return {
        "product_nm": "테스트상품1"
        # gubun 필드 누락
    }
