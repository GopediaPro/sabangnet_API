import pytest
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.receive_orders.receive_order_create_service import ReceiveOrderCreateService
from api.v1.endpoints.receive_order import get_receive_order_read_service, get_receive_order_create_service


@pytest.fixture
def mock_receive_order_read_service(test_app):
    """ReceiveOrderReadService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=ReceiveOrderReadService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_receive_order_read_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_receive_order_create_service(test_app):
    """ReceiveOrderCreateService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=ReceiveOrderCreateService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_receive_order_create_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_receive_order_list():
    """테스트용 주문 수집 목록"""
    return MOCK_TABLES["receive_orders"]