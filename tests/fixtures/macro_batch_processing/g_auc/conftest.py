import pytest
import pandas as pd
from typing import Any
from tests.mocks import MOCK_TABLES
from unittest.mock import patch, AsyncMock
from utils.logs.sabangnet_logger import get_logger
from services.usecase.data_processing_usecase import DataProcessingUsecase

from utils.macros.data_processing_utils import DataProcessingUtils
from tests.fixtures.macro_batch_processing.g_auc.expect_dataframe import create_expect_dataframes
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
        expect_dataframe_okclbb = create_expect_dataframes()["OK,CL,BB_m"]
        expect_dataframes_iy = create_expect_dataframes()["IY_m"]

        sample_dict = df.to_dict()
        expect_dict_okclbb = expect_dataframe_okclbb.to_dict()
        expect_dict_iy = expect_dataframes_iy.to_dict()

        sample_raw_data: list[dict[str, Any]] = await DataProcessingUtils.process_excel_data(df, config, work_status) 

        # 3. DB 저장 (테스트)
        objects = [row for row in sample_raw_data]
        MOCK_TABLES["down_form_orders"].extend(objects)
        logger.info(f"[END] process_excel_to_down_form_orders | saved_count={len(objects)}")
        return {
            "saved_count": len(objects),
            "sample_dict": sample_dict,
            "expect_dict_okclbb": expect_dict_okclbb,
            "expect_dict_iy": expect_dict_iy
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
    테스트용 upload_excel_file_to_macro_get_url 요청 데이터
    """

    df = create_test_dataframe()
    excel_buffer = create_test_excel_in_memory(df)
    upload_file = create_multipart_upload_file(excel_buffer)

    return {
        "template_code": "gmarket_erp",
        "file": upload_file
    }
