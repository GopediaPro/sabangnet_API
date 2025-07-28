import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.export_templates.export_templates_read_service import ExportTemplatesReadService
from services.down_form_orders.template_config_read_service import TemplateConfigReadService
from repository.export_templates_repository import ExportTemplateRepository
from repository.template_config_repository import TemplateConfigRepository
from models.config.export_templates import ExportTemplates
from models.macro_batch_processing.macro_info import MacroInfo
from fastapi import UploadFile
import io


@pytest.fixture
async def mock_session():
    """실제 DB 세션을 모킹"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
async def mock_export_templates_repository(mock_session):
    """실제 DB 데이터를 반환하는 repository 모킹"""
    repository = ExportTemplateRepository(mock_session)
    
    # 실제 DB 데이터를 반환하도록 설정
    async def mock_get_export_templates():
        return [
            ExportTemplates(
                id=22, template_code="star_brandi_bundle", template_name="스타배송-브랜디 합포장용",
                site_type="브랜디", usage_type="합포장용", is_star=True, is_active=True
            ),
            ExportTemplates(
                id=5, template_code="basic_erp", template_name="알리 지그재그 기타사이트 ERP용",
                site_type="기본양식", usage_type="ERP용", is_star=False, is_active=True
            ),
            ExportTemplates(
                id=4, template_code="gmarket_erp", template_name="G마켓,옥션 ERP용",
                site_type="G마켓,옥션", usage_type="ERP용", is_star=False, is_active=True
            ),
            ExportTemplates(
                id=6, template_code="brandi_erp", template_name="브랜디 ERP용",
                site_type="브랜디", usage_type="ERP용", is_star=False, is_active=True
            ),
            ExportTemplates(
                id=8, template_code="star_gmarket_erp", template_name="스타배송-G마켓,옥션 ERP용",
                site_type="G마켓,옥션", usage_type="ERP용", is_star=True, is_active=True
            ),
            ExportTemplates(
                id=9, template_code="star_basic_erp", template_name="스타배송-기본양식 ERP용",
                site_type="기본양식", usage_type="ERP용", is_star=True, is_active=True
            ),
            ExportTemplates(
                id=17, template_code="gmarket_bundle", template_name="G마켓,옥션 합포장용",
                site_type="G마켓,옥션", usage_type="합포장용", is_star=False, is_active=True
            ),
            ExportTemplates(
                id=18, template_code="basic_bundle", template_name="기본양식 합포장용",
                site_type="기본양식", usage_type="합포장용", is_star=False, is_active=True
            ),
            ExportTemplates(
                id=20, template_code="star_gmarket_bundle", template_name="스타배송-G마켓,옥션 합포장용",
                site_type="G마켓,옥션", usage_type="합포장용", is_star=True, is_active=True
            ),
            ExportTemplates(
                id=21, template_code="star_basic_bundle", template_name="스타배송-기본양식 합포장용",
                site_type="기본양식", usage_type="합포장용", is_star=True, is_active=True
            )
        ]
    
    async def mock_find_template_code_by_site_usage_star(site_type: str, usage_type: str, is_star: bool):
        templates = await mock_get_export_templates()
        for template in templates:
            if (template.site_type == site_type and 
                template.usage_type == usage_type and 
                template.is_star == is_star):
                return template.template_code
        return None
    
    repository.get_export_templates = mock_get_export_templates
    repository.find_template_code_by_site_usage_star = mock_find_template_code_by_site_usage_star
    return repository


@pytest.fixture
async def mock_template_config_repository(mock_session):
    """실제 DB 데이터를 반환하는 template config repository 모킹"""
    repository = TemplateConfigRepository(mock_session)
    
    # 실제 DB 데이터를 반환하도록 설정
    async def mock_get_macro_name_by_template_code_with_sub_site(template_code: str, sub_site: str):
        macro_data = {
            ("basic_erp", "기타사이트"): "ECTSiteMacro",
            ("basic_erp", "지그재그"): "ZigzagMacro",
            ("basic_bundle", "기타사이트"): "etc_site_merge_packaging",
            ("basic_bundle", "지그재그"): "zigzag_merge_packaging",
            ("star_basic_erp", "기타사이트"): "ECTSiteMacro",
            ("star_basic_erp", "지그재그"): "ZigzagMacro",
            ("star_basic_bundle", "기타사이트"): "etc_site_merge_packaging",
            ("star_basic_bundle", "지그재그"): "zigzag_merge_packaging",
        }
        return macro_data.get((template_code, sub_site))
    
    async def mock_get_macro_name_by_template_code(template_code: str):
        macro_data = {
            "gmarket_erp": "GmarketAuctionMacro",
            "brandi_erp": "BrandiMacro",
            "gmarket_bundle": "gok_merge_packaging",
            "star_gmarket_erp": "GmarketAuctionMacro",
            "star_brandi_erp": "BrandiMacro",
            "star_gmarket_bundle": "gok_merge_packaging",
            "star_brandi_bundle": "brandy_merge_packaging",
        }
        return macro_data.get(template_code)
    
    repository.get_macro_name_by_template_code_with_sub_site = mock_get_macro_name_by_template_code_with_sub_site
    repository.get_macro_name_by_template_code = mock_get_macro_name_by_template_code
    return repository


@pytest.fixture
async def mock_export_templates_read_service(mock_export_templates_repository):
    """실제 DB 데이터를 사용하는 export templates read service"""
    service = ExportTemplatesReadService(mock_export_templates_repository.session)
    service.export_template_repository = mock_export_templates_repository
    return service


@pytest.fixture
async def mock_template_config_read_service(mock_template_config_repository):
    """실제 DB 데이터를 사용하는 template config read service"""
    service = TemplateConfigReadService(mock_template_config_repository.session)
    service.template_config_repository = mock_template_config_repository
    return service


@pytest.fixture
async def data_processing_usecase(mock_session, mock_export_templates_read_service, mock_template_config_read_service):
    """실제 DB 데이터를 사용하는 data processing usecase"""
    usecase = DataProcessingUsecase(mock_session)
    usecase.export_templates_read_service = mock_export_templates_read_service
    usecase.template_config_read_service = mock_template_config_read_service
    return usecase


@pytest.fixture
def sample_excel_file():
    """테스트용 Excel 파일 생성"""
    import pandas as pd
    df = pd.DataFrame({
        'order_id': ['TEST001', 'TEST002'],
        'product_name': ['상품1', '상품2'],
        'quantity': [1, 2]
    })
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


@pytest.fixture
def mock_upload_file(sample_excel_file):
    """UploadFile 모킹"""
    file = MagicMock(spec=UploadFile)
    file.filename = "test_file.xlsx"
    file.file = sample_excel_file
    file.read = AsyncMock(return_value=sample_excel_file.getvalue())
    return file


class TestFilenameParsingWithRealDB:
    """실제 DB 데이터를 사용한 파일명 파싱 테스트"""
    
    @pytest.mark.asyncio
    async def test_parse_filename_gmarket_erp(self, data_processing_usecase):
        """G마켓,옥션 ERP용 파일명 파싱 테스트"""
        filename = "20250724_주문서확인처리_[G마켓,옥션]-ERP용.xlsx"
        result = data_processing_usecase.parse_filename(filename)
        
        assert result['site_type'] == "G마켓,옥션"
        assert result['usage_type'] == "ERP용"
        assert result['sub_site'] is None
        assert result['is_star'] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_erp_기타사이트(self, data_processing_usecase):
        """기본양식 ERP용 기타사이트 파일명 파싱 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-ERP용-기타사이트.xlsx"
        result = data_processing_usecase.parse_filename(filename)
        
        assert result['site_type'] == "기본양식"
        assert result['usage_type'] == "ERP용"
        assert result['sub_site'] == "기타사이트"
        assert result['is_star'] is False
    
    @pytest.mark.asyncio
    async def test_parse_filename_basic_erp_지그재그(self, data_processing_usecase):
        """기본양식 ERP용 지그재그 파일명 파싱 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-ERP용-지그재그.xlsx"
        result = data_processing_usecase.parse_filename(filename)
        
        assert result['site_type'] == "기본양식"
        assert result['usage_type'] == "ERP용"
        assert result['sub_site'] == "지그재그"
        assert result['is_star'] is False
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_gmarket_erp(self, data_processing_usecase):
        """G마켓,옥션 ERP용 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[G마켓,옥션]-ERP용.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "gmarket_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_erp_기타사이트(self, data_processing_usecase):
        """기본양식 ERP용 기타사이트 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-ERP용-기타사이트.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_erp_지그재그(self, data_processing_usecase):
        """기본양식 ERP용 지그재그 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-ERP용-지그재그.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_erp"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_gmarket_bundle(self, data_processing_usecase):
        """G마켓,옥션 합포장용 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[G마켓,옥션]-합포장용.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "gmarket_bundle"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_bundle_기타사이트(self, data_processing_usecase):
        """기본양식 합포장용 기타사이트 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-합포장용-기타사이트.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_bundle"
    
    @pytest.mark.asyncio
    async def test_find_template_code_by_filename_basic_bundle_지그재그(self, data_processing_usecase):
        """기본양식 합포장용 지그재그 템플릿 코드 찾기 테스트"""
        filename = "20250724_주문서확인처리_[기본양식]-합포장용-지그재그.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code == "basic_bundle"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_basic_erp_기타사이트(self, mock_template_config_read_service):
        """basic_erp + 기타사이트 매크로 이름 조회 테스트"""
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site("basic_erp", "기타사이트")
        assert macro_name == "ECTSiteMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_with_sub_site_basic_erp_지그재그(self, mock_template_config_read_service):
        """basic_erp + 지그재그 매크로 이름 조회 테스트"""
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code_with_sub_site("basic_erp", "지그재그")
        assert macro_name == "ZigzagMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_gmarket_erp(self, mock_template_config_read_service):
        """gmarket_erp 매크로 이름 조회 테스트"""
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code("gmarket_erp")
        assert macro_name == "GmarketAuctionMacro"
    
    @pytest.mark.asyncio
    async def test_get_macro_name_by_template_code_brandi_erp(self, mock_template_config_read_service):
        """brandi_erp 매크로 이름 조회 테스트"""
        macro_name = await mock_template_config_read_service.get_macro_name_by_template_code("brandi_erp")
        assert macro_name == "BrandiMacro"
    
    @pytest.mark.asyncio
    async def test_run_macro_with_file_basic_erp_기타사이트(self, data_processing_usecase, mock_upload_file):
        """basic_erp + 기타사이트 매크로 실행 테스트"""
        with patch('services.usecase.data_processing_usecase.run_macro') as mock_run_macro:
            mock_run_macro.return_value = "ECTSiteMacro_result"
            
            result = await data_processing_usecase.run_macro_with_file("basic_erp", "test_path.xlsx", "기타사이트")
            
            assert result == "ECTSiteMacro_result"
            mock_run_macro.assert_called_once_with("ECTSiteMacro", "test_path.xlsx")
    
    @pytest.mark.asyncio
    async def test_run_macro_with_file_gmarket_erp(self, data_processing_usecase, mock_upload_file):
        """gmarket_erp 매크로 실행 테스트"""
        with patch('services.usecase.data_processing_usecase.run_macro') as mock_run_macro:
            mock_run_macro.return_value = "GmarketAuctionMacro_result"
            
            result = await data_processing_usecase.run_macro_with_file("gmarket_erp", "test_path.xlsx")
            
            assert result == "GmarketAuctionMacro_result"
            mock_run_macro.assert_called_once_with("GmarketAuctionMacro", "test_path.xlsx")
    
    @pytest.mark.asyncio
    async def test_process_macro_with_tempfile_basic_erp_기타사이트(self, data_processing_usecase, mock_upload_file):
        """basic_erp + 기타사이트 매크로 처리 테스트"""
        with patch('services.usecase.data_processing_usecase.run_macro') as mock_run_macro:
            mock_run_macro.return_value = "ECTSiteMacro_result"
            
            file_name, file_path = await data_processing_usecase.process_macro_with_tempfile("basic_erp", mock_upload_file, "기타사이트")
            
            assert file_name is not None
            assert file_path is not None
            mock_run_macro.assert_called_once_with("ECTSiteMacro", file_path)
    
    @pytest.mark.asyncio
    async def test_process_macro_with_tempfile_gmarket_erp(self, data_processing_usecase, mock_upload_file):
        """gmarket_erp 매크로 처리 테스트"""
        with patch('services.usecase.data_processing_usecase.run_macro') as mock_run_macro:
            mock_run_macro.return_value = "GmarketAuctionMacro_result"
            
            file_name, file_path = await data_processing_usecase.process_macro_with_tempfile("gmarket_erp", mock_upload_file)
            
            assert file_name is not None
            assert file_path is not None
            mock_run_macro.assert_called_once_with("GmarketAuctionMacro", file_path)
    
    @pytest.mark.asyncio
    async def test_invalid_filename_format(self, data_processing_usecase):
        """잘못된 파일명 형식 테스트"""
        filename = "invalid_filename.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code is None
    
    @pytest.mark.asyncio
    async def test_template_not_found(self, data_processing_usecase):
        """존재하지 않는 템플릿 테스트"""
        filename = "20250724_주문서확인처리_[존재하지않는사이트]-ERP용.xlsx"
        template_code = await data_processing_usecase.find_template_code_by_filename(filename)
        
        assert template_code is None 