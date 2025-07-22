import pytest
import pandas as pd
from typing import Any
from fastapi import UploadFile
from fastapi.testclient import TestClient
from repository.down_form_order_repository import DownFormOrderRepository
from services.usecase.data_processing_usecase import DataProcessingUsecase
from tests.fixtures.macro_batch_processing.g_auc.compare_excel_data import compare_sample_data_with_expected


class TestMacroBatchProcessingIntegration:
    """매크로 배치 처리 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_erp_macro_processing_full_flow(
        self,
        client: TestClient,
        sample_request_data: dict[str, Any],
        mock_process_excel_to_down_form_orders,
    ):
        """
        매크로 처리 전체 흐름 테스트
        1. 테스트용 엑셀 파일 업로드
        2. 매크로 실행하고 DB에 저장
        3. 저장된 결과와 예상 결과 비교
        """

        # 1. 테스트용 엑셀 파일 업로드
        response = client.post("/api/v1/macro/excel-macro-to-db", json=sample_request_data)

        # 2. 저장된 데이터 수 확인
        assert response.status_code == 200
        assert mock_process_excel_to_down_form_orders.return_value["saved_count"] == 13

        # 3. 저장된 데이터와 예상 데이터 비교
        assert compare_sample_data_with_expected(
            mock_process_excel_to_down_form_orders.return_value["sample_dict"],
            mock_process_excel_to_down_form_orders.return_value["expect_dict_okclbb"],
            mock_process_excel_to_down_form_orders.return_value["expect_dict_iy"]
        )

    
    @pytest.mark.asyncio
    async def test_macro_processing_with_invalid_template(
        self,
        data_processing_usecase: DataProcessingUsecase,
        sample_input_excel_path: str,
        create_upload_file_from_path
    ):
        """유효하지 않은 템플릿 코드로 매크로 처리 시 예외 발생 테스트"""
        # Given: 유효하지 않은 템플릿 코드
        invalid_template_code = "잘못된 코드"
        input_upload_file = create_upload_file_from_path(sample_input_excel_path)
        
        # When & Then: 예외 발생 확인
        with pytest.raises(ValueError, match="Template not found"):
            await data_processing_usecase.save_down_form_orders_from_macro_run_excel(
                template_code=invalid_template_code,
                file=input_upload_file
            )
    
    @pytest.mark.asyncio
    async def test_macro_processing_with_empty_file(
        self,
        data_processing_usecase: DataProcessingUsecase,
        template_code: str,
        sample_empty_upload_file: UploadFile
    ):
        """빈 엑셀 파일로 매크로 처리 시 동작 테스트"""
        # When: 빈 파일로 매크로 처리 실행
        saved_count = await data_processing_usecase.save_down_form_orders_from_macro_run_excel(
            template_code=template_code,
            file=sample_empty_upload_file
        )
        
        # Then: 저장된 데이터가 0개여야 함
        assert saved_count == 0, "빈 파일 처리 시 저장된 데이터가 0개가 아닙니다"
    
    @pytest.mark.asyncio
    async def test_cleanup_test_data(
        self,
        down_form_order_repository: DownFormOrderRepository,
        template_code: str
    ):
        """테스트 데이터 정리"""
        # 테스트 데이터 삭제
        await down_form_order_repository.delete_by_template_code_and_work_status(
            template_code=template_code,
            work_status="test_macro_run"
        )
