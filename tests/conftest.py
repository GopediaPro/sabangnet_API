"""
pytest 설정, 픽스처 정의 파일
fatapi 의 main.py 및 다른 설정 파일들과 같은 역할을 함
다른 모듈에서 임포트 하지 않아도 pytest 가 자동으로 인식하고 적용시킴
"""

import re
import os
import sys
import subprocess


if sys.platform == "win32":
    try:
        import ctypes
        # 콘솔 코드페이지를 65001(UTF-8)로 강제
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass


import pytest
import asyncio
from contextlib import asynccontextmanager

from io import BytesIO
from fastapi import FastAPI
from typing import Generator, Any
from asyncio import AbstractEventLoop
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


# pytest-asyncio 설정
pytest_plugins = ["pytest_asyncio"]


# Alembic 마이그레이션을 테스트 DB에 자동 적용하는 fixture 추가
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """테스트용 DB에 Alembic 마이그레이션 적용"""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        logger.info("Alembic 마이그레이션 적용 완료")
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.lower() if e.stderr else ""
        
        # 무시 가능한 에러 패턴들 (정규식)
        ignorable_patterns = [
            r"does not exist",
            r"already exists",
            # r"undefinedtable",
            # r"duplicate key",
            # r"constraint.*already exists"
        ]
        
        # 패턴 중 하나라도 매치되면 무시
        is_ignorable = any(re.search(pattern, error_output) for pattern in ignorable_patterns)
        
        if is_ignorable:
            logger.warning(f"마이그레이션 에러 무시: {e.stderr}")
        else:
            logger.error(f"마이그레이션 실패: {e.stderr}")
            raise
    except Exception as e:
        logger.warning(f"마이그레이션 오류 무시: {e}")


# 테스트용 lifespan 함수 (create_tables 제외)
@asynccontextmanager
async def test_lifespan(app: FastAPI):
    # 테스트에서는 create_tables를 실행하지 않음
    yield
    # 테스트 종료 후 정리 작업 (필요시)


# 테스트 환경 설정
@pytest.fixture(scope="session")
def set_test_environment() -> None:
    """테스트용 더미 환경변수 설정"""
    
    test_env_vars = {
        # 사방넷 관련 설정
        "SABANG_COMPANY_ID": "test_company_id",
        "SABANG_AUTH_KEY": "test_auth_key",
        "SABANG_ADMIN_URL": "https://test.admin.url",
        
        # MinIO 관련 설정
        "MINIO_ROOT_USER": "test_root_user",
        "MINIO_ROOT_PASSWORD": "test_root_password",
        "MINIO_ACCESS_KEY": "test_access_key",
        "MINIO_SECRET_KEY": "test_secret_key",
        "MINIO_ENDPOINT": "test.endpoint",
        "MINIO_BUCKET_NAME": "test_bucket",
        "MINIO_USE_SSL": "false",
        "MINIO_PORT": "9000",
        
        # 데이터베이스 관련 설정
        "DB_HOST": "test.host",
        "DB_PORT": "5432",
        "DB_NAME": "test_db",
        "DB_USER": "test_db_user",
        "DB_PASSWORD": "test_db_password",
        "DB_SSLMODE": "disable",
        "DB_TEST_TABLE": "test_table",
        "DB_TEST_COLUMN": "test_column",
        
        # FastAPI 관련 설정
        "FASTAPI_HOST": "test.host",
        "FASTAPI_PORT": "8000",
        
        # N8N 관련 설정
        "N8N_WEBHOOK_BASE_URL": "https://test.webhook-base.url",
        "N8N_WEBHOOK_PATH": "test-webhook-path",
        
        # 테스트 모드 설정
        "COMPANY_GOODS_CD_TEST_MODE": "true",
        
        # 기타 설정
        "DEPLOY_ENV": "test"
    }
    
    for key, value in test_env_vars.items():
        os.environ.setdefault(key, value)
    
    logger.info("테스트 환경변수 설정 완료")


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    """이벤트 루프 픽스처 (비동기 테스트용)"""

    # 기존 이벤트 루프 정리
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
    except RuntimeError:
        pass

    # 새 이벤트 루프 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    yield loop
    
    # 정리
    try:
        pending = asyncio.all_tasks(loop)
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
    except Exception as e:
        logger.warning(f"이벤트 루프 정리 중 경고: {e}")


@pytest.fixture
def test_app() -> FastAPI:
    """FastAPI 앱 픽스처(lifespan 모킹)"""

    try:
        # lifespan을 테스트용으로 교체
        app.router.lifespan_context = test_lifespan
        
        return app
    except Exception as e:
        logger.error(f"fastapi app import 실패: {e}")
        raise e


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, Any, None]:
    """동기 테스트 클라이언트"""

    try:
        # 의존성 함수들 mock으로 override
        from unittest.mock import AsyncMock, MagicMock
        
        # 전역 mock 인스턴스들을 저장할 딕셔너리
        global_mocks = {}
        
        # Product 관련 의존성
        from api.v1.endpoints.product import get_product_read_service, get_product_update_service, get_product_db_xml_usecase
        from services.product.product_read_service import ProductReadService
        from services.product.product_update_service import ProductUpdateService
        from services.usecase.product_db_xml_usecase import ProductDbXmlUsecase
        
        mock_product_read_service = AsyncMock(spec=ProductReadService)
        mock_product_update_service = AsyncMock(spec=ProductUpdateService)
        mock_product_db_xml_usecase = AsyncMock(spec=ProductDbXmlUsecase)
        
        global_mocks['product_read'] = mock_product_read_service
        global_mocks['product_update'] = mock_product_update_service
        global_mocks['product_db_xml'] = mock_product_db_xml_usecase
        
        test_app.dependency_overrides[get_product_read_service] = lambda: global_mocks['product_read']
        test_app.dependency_overrides[get_product_update_service] = lambda: global_mocks['product_update']
        test_app.dependency_overrides[get_product_db_xml_usecase] = lambda: global_mocks['product_db_xml']
        
        # ReceiveOrder 관련 의존성
        from api.v1.endpoints.receive_order import get_receive_order_read_service, get_receive_order_create_service
        from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
        from services.receive_orders.receive_order_create_service import ReceiveOrderCreateService
        
        mock_receive_order_read_service = AsyncMock(spec=ReceiveOrderReadService)
        mock_receive_order_create_service = AsyncMock(spec=ReceiveOrderCreateService)
        
        global_mocks['receive_order_read'] = mock_receive_order_read_service
        global_mocks['receive_order_create'] = mock_receive_order_create_service
        
        test_app.dependency_overrides[get_receive_order_read_service] = lambda: global_mocks['receive_order_read']
        test_app.dependency_overrides[get_receive_order_create_service] = lambda: global_mocks['receive_order_create']
        
        # DownFormOrder 관련 의존성
        from api.v1.endpoints.down_form_order import (
            # get_down_form_order_create_service, 
            # get_down_form_order_read_service,
            get_down_form_order_update_service,
            get_down_form_order_delete_service,
            get_data_processing_usecase
        )
        # from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
        # from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
        from services.down_form_orders.down_form_order_update_service import DownFormOrderUpdateService
        from services.down_form_orders.down_form_order_delete_service import DownFormOrderDeleteService
        # from services.usecase.data_processing_usecase import DataProcessingUsecase
        
        # mock_down_form_order_create_service = AsyncMock(spec=DownFormOrderCreateService)
        # mock_down_form_order_read_service = AsyncMock(spec=DownFormOrderReadService)
        mock_down_form_order_update_service = AsyncMock(spec=DownFormOrderUpdateService)
        mock_down_form_order_delete_service = AsyncMock(spec=DownFormOrderDeleteService)
        # mock_data_processing_usecase = AsyncMock(spec=DataProcessingUsecase)
        
        # global_mocks['down_form_order_create'] = mock_down_form_order_create_service
        # global_mocks['down_form_order_read'] = mock_down_form_order_read_service
        global_mocks['down_form_order_update'] = mock_down_form_order_update_service
        global_mocks['down_form_order_delete'] = mock_down_form_order_delete_service
        # global_mocks['data_processing'] = mock_data_processing_usecase
        
        # test_app.dependency_overrides[get_down_form_order_create_service] = lambda: global_mocks['down_form_order_create']
        # test_app.dependency_overrides[get_down_form_order_read_service] = lambda: global_mocks['down_form_order_read']
        test_app.dependency_overrides[get_down_form_order_update_service] = lambda: global_mocks['down_form_order_update']
        test_app.dependency_overrides[get_down_form_order_delete_service] = lambda: global_mocks['down_form_order_delete']
        # test_app.dependency_overrides[get_data_processing_usecase] = lambda: global_mocks['data_processing']
        
        # 전역 mock을 앱에 저장하여 테스트에서 접근 가능하도록 함
        test_app.state.global_mocks = global_mocks
        
        with TestClient(test_app) as test_client:
            yield test_client
    except Exception as e:
        logger.error(f"동기 테스트 클라이언트 호출 실패: {e}")
        raise e


# @pytest.fixture
# def async_client(test_app: FastAPI) -> TestClient:
#     """비동기 테스트 클라이언트 (TestClient 사용)"""

#     try:
#         # DataProcessingUsecase 의존성 오버라이드
#         from services.usecase.data_processing_usecase import DataProcessingUsecase
#         from unittest.mock import AsyncMock
        
#         mock_data_processing_usecase = AsyncMock(spec=DataProcessingUsecase)
#         mock_data_processing_usecase.process_excel_to_down_form_orders = AsyncMock(return_value=5)
        
#         # 함수 참조로 오버라이드
#         from api.v1.endpoints.down_form_order import get_data_processing_usecase
#         test_app.dependency_overrides[get_data_processing_usecase] = lambda: mock_data_processing_usecase
        
#         return TestClient(test_app)
#     except Exception as e:
#         logger.error(f"비동기 테스트 클라이언트 호출 실패: {e}")
#         raise e


@pytest.fixture(autouse=True)
def mock_database_connections() -> Generator[MagicMock, Any, None]:
    """데이터베이스 연결 모킹 (자동 적용)"""
    
    try:
        # 데이터베이스 관련 모든 모듈 모킹
        with patch('core.db.get_async_session') as mock_session, \
             patch('core.db.async_engine') as mock_engine, \
             patch('core.db.get_db_pool') as mock_get_db, \
             patch('core.db.AsyncSessionLocal') as mock_session_local, \
             patch('core.db.test_db_write') as mock_test_db_write, \
             patch('core.db.close_db_pool') as mock_close_db_pool, \
             patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_create_engine, \
             patch('asyncpg.create_pool') as mock_create_pool:
            
            # 세션 모킹
            mock_session.return_value = MagicMock()
            
            # 엔진 모킹
            mock_engine_instance = MagicMock()
            mock_engine_instance.begin = AsyncMock()
            mock_engine.return_value = mock_engine_instance
            
            # 세션 로컬 모킹
            mock_session_local_instance = MagicMock()
            mock_session_local_instance.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session_local_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_local_instance
            
            # DB 컨텍스트 매니저 모킹
            mock_db_context = MagicMock()
            mock_db_context.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_db_context.__aexit__ = AsyncMock(return_value=None)
            mock_get_db.return_value = mock_db_context
            
            # 테스트 DB 쓰기 모킹
            mock_test_db_write.return_value = True
            
            # DB 풀 종료 모킹
            mock_close_db_pool.return_value = None
            
            # 엔진 생성 모킹
            mock_create_engine.return_value = mock_engine_instance
            
            # 풀 생성 모킹
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_pool.close = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            yield mock_session
    except Exception as e:
        logger.error(f"테스트 db 연결 모킹 실패: {e}")
        raise e


@pytest.fixture
def mock_external_api() -> MagicMock:
    """외부 API 모킹"""

    try:
        mock_api = MagicMock()
        mock_api.get = AsyncMock(return_value={"status": "success", "data": {}})
        mock_api.post = AsyncMock(return_value={"status": "success", "data": {}})
        mock_api.put = AsyncMock(return_value={"status": "success", "data": {}})
        mock_api.delete = AsyncMock(return_value={"status": "success", "data": {}})
        return mock_api
    except Exception as e:
        logger.error(f"외부 API 모킹 생성 실패: {e}")
        raise e


@pytest.fixture
def mock_file_upload() -> MagicMock:
    """파일 업로드 모킹"""
    
    try:
        mock_file = MagicMock()
        mock_file.filename = "test_file.xlsx"
        mock_file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        mock_file.file = BytesIO(b"test file content")
        mock_file.read = AsyncMock(return_value=b"test file content")
        return mock_file
    except Exception as e:
        logger.error(f"파일 업로드 모킹 생성 실패: {e}")
        raise e


@pytest.fixture
def mock_minio_client() -> MagicMock:
    """MinIO 클라이언트 모킹"""
    
    try:
        mock_minio = MagicMock()
        mock_minio.put_object = AsyncMock(return_value=None)
        mock_minio.get_object = AsyncMock(return_value=BytesIO(b"test content"))
        mock_minio.remove_object = AsyncMock(return_value=None)
        mock_minio.presigned_get_object = MagicMock(return_value="https://test.com/file")
        return mock_minio
    except Exception as e:
        logger.error(f"MinIO 클라이언트 모킹 생성 실패: {e}")
        raise e


@pytest.fixture
def mock_httpx_client() -> MagicMock:
    """httpx 클라이언트 모킹"""
    
    try:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
        mock_response.text = "success"
        
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.put = AsyncMock(return_value=mock_response)
        mock_client.delete = AsyncMock(return_value=mock_response)
        
        return mock_client
    except Exception as e:
        logger.error(f"httpx 클라이언트 모킹 생성 실패: {e}")
        raise e


# 테스트 마커 설정
def pytest_configure(config: pytest.Config) -> None:
    """pytest 설정"""
    
    try:
        config.addinivalue_line(
            "markers", "unit: 단위 테스트"
        )
        config.addinivalue_line(
            "markers", "integration: 통합 테스트"
        )
        config.addinivalue_line(
            "markers", "api: API 테스트"
        )
        config.addinivalue_line(
            "markers", "db: 데이터베이스 관련 테스트"
        )
        config.addinivalue_line(
            "markers", "external: 외부 서비스 의존 테스트"
        )
        config.addinivalue_line(
            "markers", "asyncio: 비동기 테스트"
        )
        
        logger.info("pytest 마커 설정 완료")
    except Exception as e:
        logger.error(f"pytest 마커 설정 실패: {e}")
        raise e


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """테스트 수집 후 아이템 수정"""
    
    try:
        # 비동기 테스트에 asyncio 마커 자동 추가
        for item in items:
            if asyncio.iscoroutinefunction(item.function):
                item.add_marker(pytest.mark.asyncio)
        
        logger.info("테스트 아이템 수정 완료")
    except Exception as e:
        logger.error(f"테스트 아이템 수정 실패: {e}")
        raise e
