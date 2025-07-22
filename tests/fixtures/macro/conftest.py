import pytest
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock
from services.batch_info_service import BatchInfoService
from api.v1.endpoints.macro import get_batch_info_service


@pytest.fixture
def mock_batch_info_service(test_app):
    """BatchInfoService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=BatchInfoService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_batch_info_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_mall_info_list():
    """테스트용 배치 정보 목록"""
    return MOCK_TABLES["mall_info"]
