import pytest
from tests.mocks import MOCK_TABLES
from unittest.mock import AsyncMock, MagicMock, patch
from services.product.product_read_service import ProductReadService
from services.product.product_update_service import ProductUpdateService
from services.usecase.product_db_xml_usecase import ProductDbXmlUsecase
from utils.make_xml.product_registration_xml import ProductRegistrationXml
from api.v1.endpoints.product_bulk_tool import get_product_read_service, get_product_update_service, get_product_db_xml_usecase


@pytest.fixture
def mock_product_read_service(test_app):
    """ProductReadService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=ProductReadService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_read_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_product_update_service(test_app):
    """ProductUpdateService 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_service = AsyncMock(spec=ProductUpdateService)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_update_service] = lambda: mock_service
    
    yield mock_service
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_product_db_xml_usecase(test_app):
    """ProductDbXmlUsecase 모킹"""
    
    # AsyncMock 인스턴스 생성
    mock_usecase = AsyncMock(spec=ProductDbXmlUsecase)
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_product_db_xml_usecase] = lambda: mock_usecase
    
    yield mock_usecase
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_upload_file_to_minio(test_app):
    """upload_file_to_minio 함수 모킹"""
    with patch('api.v1.endpoints.product.upload_file_to_minio', new_callable=MagicMock) as mock:
        mock.return_value = "test_xml_file.xml"
        yield mock


@pytest.fixture
def mock_get_minio_file_url(test_app):
    """get_minio_file_url 함수 모킹"""
    with patch('api.v1.endpoints.product.get_minio_file_url', new_callable=MagicMock) as mock:
        mock.return_value = "http://example.com/xml"
        yield mock


@pytest.fixture
def mock_product_create_service_request(test_app):
    """ProductCreateService.request_product_create_via_url 메서드 모킹"""
    with patch('services.product.product_create_service.ProductCreateService.request_product_create_via_url') as mock:
        mock.return_value = """
        <SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
            <DATA>
                <PRODUCT_ID>12345</PRODUCT_ID>
                <COMPAYNY_GOODS_CD>GOODS001</COMPAYNY_GOODS_CD>
            </DATA>
        </SABANGNET_PRODUCT_REGISTRATION_RESPONSE>
        """
        yield mock


@pytest.fixture
def mock_product_registration_xml(test_app):
    """ProductRegistrationXml 모킹"""
    with patch('api.v1.endpoints.product.ProductRegistrationXml') as mock_class:
        mock_instance = AsyncMock(spec=ProductRegistrationXml)
        mock_instance.input_product_id_to_db.return_value = [("GOODS001", 12345)]
        mock_class.return_value = mock_instance
        yield mock_class


@pytest.fixture
def sample_product_list():
    return MOCK_TABLES["product_raw_data"]