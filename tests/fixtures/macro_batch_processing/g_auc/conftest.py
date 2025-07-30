import pytest
import pandas as pd
import io
from typing import Any
from fastapi import UploadFile
from tests.mocks import MOCK_TABLES
from unittest.mock import patch, AsyncMock
from utils.logs.sabangnet_logger import get_logger
from services.usecase.data_processing_usecase import DataProcessingUsecase
from repository.down_form_order_repository import DownFormOrderRepository
from api.v1.endpoints.macro import get_data_processing_usecase

from utils.macros.data_processing_utils import DataProcessingUtils
from tests.fixtures.macro_batch_processing.g_auc.expect_dataframe import create_expect_dataframe
from tests.fixtures.macro_batch_processing.g_auc.sample_excel_file import (
    create_multipart_upload_file,
    create_test_excel_in_memory,
    create_test_dataframe
)


logger = get_logger(__name__)


@pytest.fixture
def mock_process_excel_to_down_form_orders(test_app):
    """DataProcessingUsecase 의 process_excel_to_down_form_orders 모킹"""

    mock = AsyncMock()

    async def _mock_process_excel_to_down_form_orders(
            self,
            df: pd.DataFrame,
            template_code: str,
            work_status: str = None
    ) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
        """
        들어온 processed_data와 기대 결과를 가져와서 비교함.
        """

        logger.info(f"[START] process_excel_to_down_form_orders | template_code={template_code} | df_count={len(df)}")

        # 1. config 매핑 정보 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        logger.info(f"Loaded template config: {config}")

        # 2. 엑셀 데이터 변환
        expect_dataframe = create_expect_dataframe()

        sample_dict = df.to_dict()
        expect_dict = expect_dataframe.to_dict()

        sample_raw_data: list[dict[str, Any]] = await DataProcessingUtils.process_excel_data(df, config, work_status) 

        # 3. DB 저장 (테스트)
        objects = [row for row in sample_raw_data]
        MOCK_TABLES["down_form_orders"].extend(objects)
        logger.info(f"[END] process_excel_to_down_form_orders | saved_count={len(objects)}")
        return {
            "saved_count": len(objects),
            "sample_dict": sample_dict,
            "expect_dict": expect_dict
        }
    
    mock.side_effect = _mock_process_excel_to_down_form_orders

    with patch.object(
        DataProcessingUsecase,
        "process_excel_to_down_form_orders",
        mock,
    ):
        yield mock


@pytest.fixture
def sample_request_data():
    """
    테스트용 매크로 요청 데이터 (JSON 직렬화 가능한 형태)
    """
    return {
        "template_code": "gmarket_erp",
        "filters": {
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "mall_id": "test_mall"
        }
    }


@pytest.fixture
def data_processing_usecase(test_app):
    """DataProcessingUsecase fixture"""
    # 실제 서비스 인스턴스 생성 (테스트용)
    mock_usecase = AsyncMock(spec=DataProcessingUsecase)
    
    # Mock 메서드들의 반환값 설정
    mock_usecase.save_down_form_orders_from_macro_run_excel.return_value = 13  # 기본값을 13으로 변경
    mock_usecase.get_excel_run_macro_minio_url.return_value = {
        "success": True,
        "template_code": "gmarket_erp",
        "batch_id": "test_batch_id",
        "file_url": "http://example.com/test.xlsx",
        "minio_object_name": "test.xlsx"
    }
    
    # 유효하지 않은 템플릿에 대한 예외 설정
    async def mock_save_with_invalid_template(*args, **kwargs):
        template_code = kwargs.get('template_code', args[1] if len(args) > 1 else None)
        if template_code == "잘못된 코드":
            raise ValueError("Template not found")
        return 0
    
    mock_usecase.save_down_form_orders_from_macro_run_excel.side_effect = mock_save_with_invalid_template
    
    # 의존성 오버라이드
    test_app.dependency_overrides[get_data_processing_usecase] = lambda: mock_usecase
    
    yield mock_usecase
    
    # 정리
    test_app.dependency_overrides.clear()


@pytest.fixture
def down_form_order_repository(test_app):
    """DownFormOrderRepository fixture"""
    # 실제 repository 인스턴스 생성 (테스트용)
    mock_repository = AsyncMock(spec=DownFormOrderRepository)
    
    # 누락된 메서드 추가
    mock_repository.delete_by_template_code_and_work_status = AsyncMock()
    mock_repository.delete_by_template_code_and_work_status.return_value = 0
    
    yield mock_repository


@pytest.fixture
def sample_input_excel_path(tmp_path):
    """테스트용 엑셀 파일 경로"""
    # 임시 엑셀 파일 생성
    excel_file = tmp_path / "test_input.xlsx"
    
    # 간단한 테스트 데이터로 엑셀 파일 생성
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['test1', 'test2', 'test3'],
        'C': [100, 200, 300]
    })
    
    df.to_excel(excel_file, index=False)
    return str(excel_file)


@pytest.fixture
def create_upload_file_from_path():
    """경로로부터 UploadFile 생성하는 fixture"""
    def _create_upload_file(file_path: str) -> UploadFile:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        upload_file = UploadFile(
            filename="test.xlsx",
            file=io.BytesIO(content),
            size=len(content),
            headers={
                "content-disposition": 'form-data; name="file"; filename="test.xlsx"',
                "content-type": content_type
            }
        )
        
        return upload_file
    
    return _create_upload_file


@pytest.fixture
def template_code():
    """테스트용 템플릿 코드"""
    return "gmarket_erp"


@pytest.fixture
def sample_empty_upload_file():
    """빈 엑셀 파일 UploadFile"""
    # 빈 DataFrame으로 엑셀 파일 생성
    df = pd.DataFrame()
    
    # DataFrame을 Excel로 변환
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    upload_file = UploadFile(
        filename="empty.xlsx",
        file=output,
        size=len(output.getvalue()),
        headers={
            "content-disposition": 'form-data; name="file"; filename="empty.xlsx"',
            "content-type": content_type
        }
    )
    
    return upload_file
