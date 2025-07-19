import pytest
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock, patch

from api.v1.endpoints.down_form_order import get_down_form_order_create_service
from api.v1.endpoints.down_form_order import get_down_form_order_read_service
from api.v1.endpoints.down_form_order import get_down_form_order_update_service
from api.v1.endpoints.down_form_order import get_down_form_order_delete_service
from api.v1.endpoints.down_form_order import get_data_processing_usecase
from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.down_form_order_update_service import DownFormOrderUpdateService
from services.down_form_orders.down_form_order_delete_service import DownFormOrderDeleteService
from services.usecase.data_processing_usecase import DataProcessingUsecase



@pytest.fixture
def mock_down_form_order_create_service(test_app):
    """DownFormOrderCreateService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=DownFormOrderCreateService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_down_form_order_create_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_down_form_order_read_service(test_app):
    """DownFormOrderReadService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=DownFormOrderReadService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_down_form_order_read_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_down_form_order_update_service(test_app):
    """DownFormOrderUpdateService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=DownFormOrderUpdateService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_down_form_order_update_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_down_form_order_delete_service(test_app):
    """DownFormOrderDeleteService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=DownFormOrderDeleteService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_down_form_order_delete_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_data_processing_usecase(test_app):
    """DataProcessingUsecase 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_usecase = AsyncMock(spec=DataProcessingUsecase)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_data_processing_usecase] = lambda: mock_usecase
    
    yield mock_usecase
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_temp_file_to_object_name():
    """temp_file_to_object_name 함수 모킹"""
    with patch('api.v1.endpoints.down_form_order.temp_file_to_object_name') as mock:
        mock.return_value = "temp_file_path"
        yield mock


@pytest.fixture
def mock_upload_and_get_url():
    """upload_and_get_url 함수 모킹"""
    with patch('api.v1.endpoints.down_form_order.upload_and_get_url') as mock:
        mock.return_value = ("http://example.com/excel.xlsx", "excel.xlsx")
        yield mock


@pytest.fixture
def mock_excel_handler():
    """ExcelHandler 클래스 모킹"""
    with patch('api.v1.endpoints.down_form_order.ExcelHandler') as mock:
        yield mock


@pytest.fixture
def sample_down_form_order_list():
    """테스트용 다운폼 주문 목록"""
    return MOCK_TABLES["down_form_orders"]


@pytest.fixture
def sample_excel_file_content():
    """테스트용 엑셀 파일 내용"""
    import io
    import pandas as pd
    
    # 테스트 엑셀
    test_data = {
        'A': [1, 2, 3, 4, 5],
        'B': ['test1', 'test2', 'test3', 'test4', 'test5'],
        'C': [100, 200, 300, 400, 500]
    }
    df = pd.DataFrame(test_data)
    
    # DataFrame을 Excel로...
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    output.seek(0)
    return output.getvalue()


@pytest.fixture
def sample_down_form_order_request_data():
    """테스트용 다운폼 주문 요청 데이터"""
    return {
        "items": [
            {
                "idx": "IDX001",
                "form_name": "테스트폼1",
                "order_id": "ORDER001",
                "product_name": "테스트상품1",
                "sale_cnt": 2,
                "pay_cost": 10000,
                "total_cost": 20000
            },
            {
                "idx": "IDX002",
                "form_name": "테스트폼2",
                "order_id": "ORDER002",
                "product_name": "테스트상품2",
                "sale_cnt": 1,
                "pay_cost": 15000,
                "total_cost": 15000
            }
        ]
    }


@pytest.fixture
def sample_down_form_order_update_request_data():
    """테스트용 다운폼 주문 수정 요청 데이터"""
    return {
        "items": [
            {
                "id": 1,
                "idx": "IDX001",
                "form_name": "수정된폼1",
                "order_id": "ORDER001",
                "product_name": "수정된상품1",
                "sale_cnt": 3,
                "pay_cost": 12000,
                "total_cost": 36000
            },
            {
                "id": 2,
                "idx": "IDX002",
                "form_name": "수정된폼2",
                "order_id": "ORDER002",
                "product_name": "수정된상품2",
                "sale_cnt": 2,
                "pay_cost": 18000,
                "total_cost": 36000
            }
        ]
    }


@pytest.fixture
def sample_down_form_order_delete_request_data():
    """테스트용 다운폼 주문 삭제 요청 데이터"""
    return {
        "ids": [1, 2, 3]
    }