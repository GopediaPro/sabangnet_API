import pytest
import pandas as pd
from typing import Any
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO
import tempfile
import os

from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.down_form_orders.template_config_read_service import TemplateConfigReadService
from services.export_templates.export_templates_read_service import ExportTemplatesReadService
from repository.template_config_repository import TemplateConfigRepository
from repository.export_templates_repository import ExportTemplateRepository
from tests.mocks.mock_macro_info import MACRO_INFO
from tests.mocks.mock_export_templates import EXPORT_TEMPLATES


class TestFilenameParsingIntegration:
    """파일명 파싱 및 매크로 매칭 통합 테스트"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock AsyncSession"""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def mock_template_config_repository(self, mock_session):
        """Mock TemplateConfigRepository"""
        repository = TemplateConfigRepository(mock_session)
        
        # Mock get_macro_name_by_template_code_with_sub_site method
        async def mock_get_macro_name_by_template_code_with_sub_site(template_code: str, sub_site: str):
            for macro in MACRO_INFO:
                if macro["form_name"] == template_code and macro["sub_site"] == sub_site:
                    return macro["macro_name"]
            return None
        
        async def mock_get_macro_name_by_template_code(template_code: str):
            for macro in MACRO_INFO:
                if macro["form_name"] == template_code and macro["sub_site"] is None:
                    return macro["macro_name"]
            return None
        
        repository.get_macro_name_by_template_code_with_sub_site = mock_get_macro_name_by_template_code_with_sub_site
        repository.get_macro_name_by_template_code = mock_get_macro_name_by_template_code
        
        return repository
    
    @pytest.fixture
    def mock_export_templates_repository(self, mock_session):
        """Mock ExportTemplateRepository"""
        repository = ExportTemplateRepository(mock_session)
        
        # Mock get_export_templates method
        async def mock_get_export_templates():
            # Convert dict to mock objects
            mock_templates = []
            for template in EXPORT_TEMPLATES:
                mock_template = MagicMock()
                mock_template.template_code = template["template_code"]
                mock_template.template_name = template["template_name"]
                mock_templates.append(mock_template)
            return mock_templates
        
        repository.get_export_templates = mock_get_export_templates
        return repository
    
    @pytest.fixture
    def mock_template_config_read_service(self, mock_template_config_repository):
        """Mock TemplateConfigReadService"""
        service = TemplateConfigReadService(MagicMock())
        service.template_config_repository = mock_template_config_repository
        return service
    
    @pytest.fixture
    def mock_export_templates_read_service(self, mock_export_templates_repository):
        """Mock ExportTemplatesReadService"""
        service = ExportTemplatesReadService(MagicMock())
        service.export_template_repository = mock_export_templates_repository
        return service
    
    @pytest.fixture
    def data_processing_usecase(self, mock_session, mock_template_config_read_service, mock_export_templates_read_service):
        """DataProcessingUsecase with mocked dependencies"""
        usecase = DataProcessingUsecase(mock_session)
        usecase.template_config_read_service = mock_template_config_read_service
        usecase.export_templates_read_service = mock_export_templates_read_service
        return usecase
    
    @pytest.fixture
    def sample_excel_file(self):
        """Create a sample Excel file for testing"""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['test1', 'test2', 'test3'],
            'C': [100, 200, 300]
        })
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            return tmp_file.name
    
    @pytest.fixture
    def mock_upload_file(self, sample_excel_file):
        """Create mock UploadFile"""
        upload_file = MagicMock(spec=UploadFile)
        upload_file.filename = "test.xlsx"
        upload_file.file = open(sample_excel_file, 'rb')
        return upload_file
    
    @pytest.mark.asyncio
    async def test_parse_filename_gmarket_erp(self, data_processing_usecase):
        """G마켓,옥션 ERP용 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[G마켓,옥션]-ERP용.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "G마켓,옥션"
        assert result["usage_type"] == "ERP용"
        assert result["sub_site"] is None
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_erp_기타사이트(self, data_processing_usecase):
        """기본양식 ERP용 기타사이트 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[기본양식]-ERP용-기타사이트.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "기본양식"
        assert result["usage_type"] == "ERP용"
        assert result["sub_site"] == "기타사이트"
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_erp_지그재그(self, data_processing_usecase):
        """기본양식 ERP용 지그재그 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[기본양식]-ERP용-지그재그.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "기본양식"
        assert result["usage_type"] == "ERP용"
        assert result["sub_site"] == "지그재그"
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_brandi_erp(self, data_processing_usecase):
        """브랜디 ERP용 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[브랜디]-ERP용.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "브랜디"
        assert result["usage_type"] == "ERP용"
        assert result["sub_site"] is None
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_gmarket_bundle(self, data_processing_usecase):
        """G마켓,옥션 합포장용 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[G마켓,옥션]-합포장용.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "G마켓,옥션"
        assert result["usage_type"] == "합포장용"
        assert result["sub_site"] is None
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_bundle_기타사이트(self, data_processing_usecase):
        """기본양식 합포장용 기타사이트 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[기본양식]-합포장용-기타사이트.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "기본양식"
        assert result["usage_type"] == "합포장용"
        assert result["sub_site"] == "기타사이트"
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_bundle_지그재그(self, data_processing_usecase):
        """기본양식 합포장용 지그재그 파일명 파싱 테스트"""
        filename = "20250724주문서확인처리[기본양식]-합포장용-지그재그.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_type"] == "기본양식"
        assert result["usage_type"] == "합포장용"
        assert result["sub_site"] == "지그재그"
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_gmarket_erp(self, data_processing_usecase):
        """G마켓,옥션 ERP용 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[G마켓,옥션]-ERP용.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "gmarket_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_erp_기타사이트(self, data_processing_usecase):
        """기본양식 ERP용 기타사이트 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[기본양식]-ERP용-기타사이트.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_erp_지그재그(self, data_processing_usecase):
        """기본양식 ERP용 지그재그 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[기본양식]-ERP용-지그재그.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_brandi_erp(self, data_processing_usecase):
        """브랜디 ERP용 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[브랜디]-ERP용.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "brandi_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_gmarket_bundle(self, data_processing_usecase):
        """G마켓,옥션 합포장용 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[G마켓,옥션]-합포장용.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "gmarket_bundle"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_bundle_기타사이트(self, data_processing_usecase):
        """기본양식 합포장용 기타사이트 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[기본양식]-합포장용-기타사이트.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_bundle"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_bundle_지그재그(self, data_processing_usecase):
        """기본양식 합포장용 지그재그 템플릿 코드 찾기 테스트"""
        filename = "20250724주문서확인처리[기본양식]-합포장용-지그재그.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_bundle"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_기타사이트(self, mock_template_config_read_service):
        """기타사이트 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_erp"
        sub_site = "기타사이트"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name == "ECTSiteMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_지그재그(self, mock_template_config_read_service):
        """지그재그 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_erp"
        sub_site = "지그재그"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name == "ZigzagMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_알리(self, mock_template_config_read_service):
        """알리 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_erp"
        sub_site = "알리"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name is None  # 알리는 실제 데이터에 없음
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_basic_bundle_기타사이트(self, mock_template_config_read_service):
        """basic_bundle 기타사이트 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_bundle"
        sub_site = "기타사이트"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name == "etc_site_merge_packaging"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_basic_bundle_지그재그(self, mock_template_config_read_service):
        """basic_bundle 지그재그 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_bundle"
        sub_site = "지그재그"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name == "zigzag_merge_packaging"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_basic_bundle_알리(self, mock_template_config_read_service):
        """basic_bundle 알리 sub_site로 매크로명 조회 테스트"""
        template_code = "basic_bundle"
        sub_site = "알리"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
        
        assert macro_name is None  # 알리는 실제 데이터에 없음
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_gmarket_erp(self, mock_template_config_read_service):
        """gmarket_erp 기본 매크로명 조회 테스트"""
        template_code = "gmarket_erp"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code(template_code)
        
        assert macro_name == "GmarketAuctionMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_brandi_erp(self, mock_template_config_read_service):
        """brandi_erp 기본 매크로명 조회 테스트"""
        template_code = "brandi_erp"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code(template_code)
        
        assert macro_name == "BrandiMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_gmarket_bundle(self, mock_template_config_read_service):
        """gmarket_bundle 기본 매크로명 조회 테스트"""
        template_code = "gmarket_bundle"
        
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code(template_code)
        
        assert macro_name == "gok_merge_packaging"
    
    @pytest.mark.asyncio
    async def test_run_macro_with_file_with_sub_site(self, data_processing_usecase, mock_upload_file):
        """sub_site가 있는 경우 매크로 실행 테스트"""
        template_code = "basic_erp"
        file_path = "/tmp/test.xlsx"
        sub_site = "기타사이트"
        
        # Mock the macro function
        mock_macro_func = MagicMock(return_value="/tmp/processed_test.xlsx")
        data_processing_usecase.order_macro_utils.MACRO_MAP = {
            "ECTSiteMacro": mock_macro_func
        }
        
        result = await data_processing_usecase.run_macro_with_file(template_code, file_path, sub_site)
        
        assert result == "/tmp/processed_test.xlsx"
        mock_macro_func.assert_called_once_with(file_path)
    
    @pytest.mark.asyncio
    async def test_run_macro_with_file_without_sub_site(self, data_processing_usecase, mock_upload_file):
        """sub_site가 없는 경우 매크로 실행 테스트"""
        template_code = "gmarket_erp"
        file_path = "/tmp/test.xlsx"
        
        # Mock the macro function
        mock_macro_func = MagicMock(return_value="/tmp/processed_test.xlsx")
        data_processing_usecase.order_macro_utils.MACRO_MAP = {
            "GmarketAuctionMacro": mock_macro_func
        }
        
        result = await data_processing_usecase.run_macro_with_file(template_code, file_path)
        
        assert result == "/tmp/processed_test.xlsx"
        mock_macro_func.assert_called_once_with(file_path)
    
    @pytest.mark.asyncio
    async def test_process_macro_with_tempfile_with_sub_site(self, data_processing_usecase, mock_upload_file):
        """sub_site가 있는 경우 임시 파일 처리 테스트"""
        template_code = "basic_erp"
        sub_site = "기타사이트"
        
        # Mock the macro function
        mock_macro_func = MagicMock(return_value="/tmp/processed_test.xlsx")
        data_processing_usecase.order_macro_utils.MACRO_MAP = {
            "ECTSiteMacro": mock_macro_func
        }
        
        # Mock temp_file_to_object_name and delete_temp_file
        with patch('services.usecase.data_processing_usecase.temp_file_to_object_name', return_value="/tmp/temp.xlsx"), \
             patch('services.usecase.data_processing_usecase.delete_temp_file'):
            
            file_name, file_path = await data_processing_usecase.process_macro_with_tempfile(template_code, mock_upload_file, sub_site)
            
            assert file_name == "test.xlsx"
            assert file_path == "/tmp/processed_test.xlsx"
    
    @pytest.mark.asyncio
    async def test_process_macro_with_tempfile_without_sub_site(self, data_processing_usecase, mock_upload_file):
        """sub_site가 없는 경우 임시 파일 처리 테스트"""
        template_code = "gmarket_erp"
        
        # Mock the macro function
        mock_macro_func = MagicMock(return_value="/tmp/processed_test.xlsx")
        data_processing_usecase.order_macro_utils.MACRO_MAP = {
            "GmarketAuctionMacro": mock_macro_func
        }
        
        # Mock temp_file_to_object_name and delete_temp_file
        with patch('services.usecase.data_processing_usecase.temp_file_to_object_name', return_value="/tmp/temp.xlsx"), \
             patch('services.usecase.data_processing_usecase.delete_temp_file'):
            
            file_name, file_path = await data_processing_usecase.process_macro_with_tempfile(template_code, mock_upload_file)
            
            assert file_name == "test.xlsx"
            assert file_path == "/tmp/processed_test.xlsx"
    
    def test_parse_filename_invalid_format(self, data_processing_usecase):
        """잘못된 형식의 파일명 파싱 테스트"""
        filename = "invalid_filename.xlsx"
        
        result = data_processing_usecase.parse_filename(filename)
        
        assert result["site_name"] is None
        assert result["usage_type"] is None
        assert result["sub_site"] is None
        assert result["is_star"] is False
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_not_found(self, data_processing_usecase):
        """찾을 수 없는 템플릿 코드 테스트"""
        filename = "20250724주문서확인처리[존재하지않는사이트]-ERP용.xlsx"
        
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code is None 