import pytest
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock
from api.v1.endpoints.mall_price import get_product_mall_price_usecase
from services.usecase.product_mall_price_usecase import ProductMallPriceUsecase


@pytest.fixture
def mock_product_mall_price_usecase(test_app):
    """ProductMallPriceUsecase 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=ProductMallPriceUsecase)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_mall_price_usecase] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_mall_price_list():
    """테스트용 매장 가격 정보 목록"""
    return MOCK_TABLES["mall_price"]
