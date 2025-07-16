import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from tests.mock_db.mock_tables.test_product_raw_data import TEST_PRODUCT_RAW_DATA
from services.product.product_read_service import ProductReadService
from services.product.product_update_service import ProductUpdateService
from services.usecase.product_db_excel_usecase import ProductDbExcelUsecase
from services.usecase.product_db_xml_usecase import ProductDbXmlUsecase


class TestProductIntegration:
    """product 엔드포인트 통합 테스트"""
    
    @pytest.fixture
    def mock_read_service(self):
        """ProductReadService 모킹"""
        with patch('api.v1.endpoints.product.ProductReadService') as mock:
            service_instance = AsyncMock()
            mock.return_value = service_instance
            yield service_instance
    
    @pytest.fixture
    def mock_update_service(self):
        """ProductUpdateService 모킹"""
        with patch('api.v1.endpoints.product.ProductUpdateService') as mock:
            service_instance = AsyncMock()
            mock.return_value = service_instance
            yield service_instance
    
    @pytest.fixture
    def mock_db_excel_usecase(self):
        """ProductDbExcelUsecase 모킹"""
        with patch('api.v1.endpoints.product.ProductDbExcelUsecase') as mock:
            usecase_instance = AsyncMock()
            mock.return_value = usecase_instance
            yield usecase_instance
    
    @pytest.fixture
    def mock_db_xml_usecase(self):
        """ProductDbXmlUsecase 모킹"""
        with patch('api.v1.endpoints.product.ProductDbXmlUsecase') as mock:
            usecase_instance = AsyncMock()
            mock.return_value = usecase_instance
            yield usecase_instance
    
    def test_get_products_success(self, client: TestClient, mock_read_service: AsyncMock):
        """상품 목록 조회 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_products = TEST_PRODUCT_RAW_DATA[:2]  # 첫 두 개 상품 데이터
        
        expected_response = {
            "products": [
                {
                    "id": product["id"],
                    "compayny_goods_cd": product["compayny_goods_cd"],
                    "product_nm": product["product_nm"],
                    "standard_price": product["standard_price"],
                    "product_id": product.get("product_id"),
                    "created_at": product.get("created_at"),
                    "updated_at": product.get("updated_at")
                }
                for product in mock_products
            ],
            "current_page": 1,
            "page_size": 20,
            "total_count": len(mock_products)
        }
        
        # Mock service의 반환값 설정
        mock_read_service.get_products_by_pagenation.return_value = [
            expected_response["products"][0],
            expected_response["products"][1]
        ]
        
        # When: API 요청 실행
        response = client.get("/api/v1/product?page=1")
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert len(response_data["products"]) == len(mock_products)
        for i, product in enumerate(response_data["products"]):
            mock_product = mock_products[i]
            assert product["compayny_goods_cd"] == mock_product["compayny_goods_cd"]
            assert product["product_nm"] == mock_product["product_nm"]
            assert product["standard_price"] == mock_product["standard_price"]
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_read_service.get_products_by_pagenation.assert_called_once_with(page=1)
    
    def test_modify_product_name_success(self, client: TestClient, mock_update_service: AsyncMock):
        """상품명 수정 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_product = TEST_PRODUCT_RAW_DATA[0]  # 첫 번째 상품 데이터
        
        request_data = {
            "compayny_goods_cd": mock_product["compayny_goods_cd"],
            "name": "수정된 상품명"
        }
        
        expected_response = {
            "message": "상품명이 성공적으로 수정되었습니다.",
            "compayny_goods_cd": mock_product["compayny_goods_cd"],
            "old_name": mock_product["product_nm"],
            "new_name": "수정된 상품명"
        }
        
        # Mock service의 반환값 설정
        mock_update_service.modify_product_name.return_value = expected_response
        
        # When: API 요청 실행
        response = client.put("/api/v1/product/name", json=request_data)
        
        # Then: 응답 검증
        assert response.status_code == 200
        response_data = response.json()
        
        # Mock DB 데이터와 일치하는지 확인
        assert response_data["compayny_goods_cd"] == mock_product["compayny_goods_cd"]
        assert response_data["old_name"] == mock_product["product_nm"]
        assert response_data["new_name"] == "수정된 상품명"
        
        # Mock이 올바른 파라미터로 호출되었는지 확인
        mock_update_service.modify_product_name.assert_called_once_with(
            compayny_goods_cd=mock_product["compayny_goods_cd"],
            product_name="수정된 상품명"
        )
    
    def test_modify_product_name_not_found(self, client: TestClient, mock_update_service: AsyncMock):
        """존재하지 않는 상품명 수정 실패 테스트"""
        # Given: 존재하지 않는 상품코드
        request_data = {
            "compayny_goods_cd": "NON_EXISTENT_GOODS",
            "name": "수정된 상품명"
        }
        
        # Mock service가 예외를 발생시키도록 설정
        mock_update_service.modify_product_name.side_effect = Exception("상품을 찾을 수 없습니다.")
        
        # When: API 요청 실행
        response = client.put("/api/v1/product/name", json=request_data)
        
        # Then: 에러 응답 검증
        assert response.status_code == 500
    
    def test_db_to_xml_sabangnet_request_all_success(self, client: TestClient, mock_db_xml_usecase: AsyncMock):
        """DB to XML 사방넷 요청 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_products = TEST_PRODUCT_RAW_DATA
        
        # Mock usecase 메서드들 설정
        mock_db_xml_usecase.db_to_xml_file_all.return_value = "/path/to/xml/file.xml"
        mock_db_xml_usecase.get_product_raw_data_count.return_value = len(mock_products)
        
        # Mock minio 업로드
        with patch('api.v1.endpoints.product.upload_file_to_minio') as mock_upload:
            with patch('api.v1.endpoints.product.get_minio_file_url') as mock_get_url:
                mock_upload.return_value = "test_xml_file.xml"
                mock_get_url.return_value = "http://example.com/xml"
                
                # Mock 사방넷 요청
                with patch('api.v1.endpoints.product.ProductCreateService.request_product_create_via_url') as mock_request:
                    with patch('api.v1.endpoints.product.ProductRegistrationXml') as mock_xml:
                        mock_request.return_value = "<response>success</response>"
                        mock_xml_instance = MagicMock()
                        mock_xml_instance.input_product_id_to_db.return_value = [
                            ("GOODS001", 12345),
                            ("GOODS002", 12346)
                        ]
                        mock_xml.return_value = mock_xml_instance
                        
                        # When: API 요청 실행
                        response = client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
                        
                        # Then: 응답 검증
                        assert response.status_code == 200
                        response_data = response.json()
                        assert response_data["success"] is True
                        assert response_data["processed_count"] == len(mock_products)
                        assert "XML로 변환하고 사방넷 상품등록 요청했습니다" in response_data["message"]
                        
                        # Mock 메서드들이 올바른 파라미터로 호출되었는지 확인
                        mock_db_xml_usecase.db_to_xml_file_all.assert_called_once()
                        mock_db_xml_usecase.get_product_raw_data_count.assert_called_once()
                        mock_db_xml_usecase.update_product_id_by_compayny_goods_cd.assert_called_once_with([
                            ("GOODS001", 12345),
                            ("GOODS002", 12346)
                        ])
    
    def test_db_to_xml_sabangnet_request_no_data(self, client: TestClient, mock_db_xml_usecase: AsyncMock):
        """데이터가 없는 경우 DB to XML 사방넷 요청 실패 테스트"""
        # Given: 데이터가 없는 상황
        mock_db_xml_usecase.db_to_xml_file_all.side_effect = ValueError("데이터가 없습니다.")
        
        # When: API 요청 실행
        response = client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
        
        # Then: 에러 응답 검증
        assert response.status_code == 404
        response_data = response.json()
        assert "데이터가 없습니다" in response_data["detail"]
    
    def test_excel_to_xml_n8n_test_success(self, client: TestClient):
        """Excel to XML N8N 테스트 성공 테스트"""
        # Given: 요청 데이터
        request_data = {
            "fileName": "test_excel_file.xlsx",
            "sheetName": "Sheet1"
        }
        
        # Mock ProductCreateService
        with patch('api.v1.endpoints.product.ProductCreateService.excel_to_xml_file') as mock_excel_to_xml:
            with patch('builtins.open') as mock_open:
                with patch('api.v1.endpoints.product.requests.post') as mock_post:
                    # Mock 파일 경로 반환
                    mock_excel_to_xml.return_value = "/path/to/xml/file.xml"
                    
                    # Mock 파일 객체
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Mock HTTP 응답
                    mock_response = MagicMock()
                    mock_response.json.return_value = {"success": True, "message": "N8N 처리 완료"}
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response
                    
                    # When: API 요청 실행
                    response = client.post("/api/v1/product/excel-to-xml-n8n-test", json=request_data)
                    
                    # Then: 응답 검증
                    assert response.status_code == 200
                    response_data = response.json()
                    assert response_data["success"] is True
                    assert "N8N 처리 완료" in response_data["message"]
    
    def test_excel_to_xml_n8n_test_file_not_found(self, client: TestClient):
        """파일을 찾을 수 없는 경우 Excel to XML N8N 테스트 실패"""
        # Given: 존재하지 않는 파일명
        request_data = {
            "fileName": "non_existent_file.xlsx",
            "sheetName": "Sheet1"
        }
        
        # Mock ProductCreateService가 FileNotFoundError 발생
        with patch('api.v1.endpoints.product.ProductCreateService.excel_to_xml_file') as mock_excel_to_xml:
            mock_excel_to_xml.side_effect = FileNotFoundError("파일을 찾을 수 없습니다")
            
            # When: API 요청 실행
            response = client.post("/api/v1/product/excel-to-xml-n8n-test", json=request_data)
            
            # Then: 에러 응답 검증
            assert response.status_code == 404
            response_data = response.json()
            assert "파일을 찾을 수 없습니다" in response_data["detail"]
    
    def test_bulk_db_to_excel_success(self, client: TestClient, mock_db_excel_usecase: AsyncMock):
        """대량 DB to Excel 변환 성공 테스트"""
        # Given: mock DB 데이터 사용
        mock_products = TEST_PRODUCT_RAW_DATA
        
        # Mock StreamingResponse
        from fastapi.responses import StreamingResponse
        mock_response = StreamingResponse(
            iter([b"excel file content"]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=products.xlsx"}
        )
        
        # Mock usecase의 반환값 설정
        mock_db_excel_usecase.convert_db_to_excel.return_value = mock_response
        
        # When: API 요청 실행
        response = client.get("/api/v1/product/bulk/db-to-excel")
        
        # Then: 응답 검증
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=products.xlsx" in response.headers["content-disposition"]
        
        # Mock이 호출되었는지 확인
        mock_db_excel_usecase.convert_db_to_excel.assert_called_once()
    
    def test_get_products_with_invalid_page(self, client: TestClient):
        """잘못된 페이지 번호로 상품 조회 실패 테스트"""
        # Given: 잘못된 페이지 번호
        invalid_pages = [0, -1]
        
        for page in invalid_pages:
            # When: API 요청 실행
            response = client.get(f"/api/v1/product?page={page}")
            
            # Then: 검증 에러 응답
            assert response.status_code == 422
    
    def test_modify_product_name_missing_fields(self, client: TestClient):
        """필수 필드 누락으로 상품명 수정 실패 테스트"""
        # Given: 필수 필드가 누락된 요청
        invalid_requests = [
            {},  # 모든 필드 누락
            {"compayny_goods_cd": "GOODS001"},  # name 필드 누락
            {"name": "새상품명"}  # compayny_goods_cd 필드 누락
        ]
        
        for request_data in invalid_requests:
            # When: API 요청 실행
            response = client.put("/api/v1/product/name", json=request_data)
            
            # Then: 검증 에러 응답
            assert response.status_code == 422
    
    def test_modify_product_name_with_mock_db_data_validation(self, client: TestClient, mock_update_service: AsyncMock):
        """mock DB 데이터 검증을 통한 상품명 수정 테스트"""
        # Given: mock DB의 모든 상품 데이터 사용
        test_products = TEST_PRODUCT_RAW_DATA[:3]  # 첫 3개 상품
        
        for i, product in enumerate(test_products):
            request_data = {
                "compayny_goods_cd": product["compayny_goods_cd"],
                "name": f"수정된 상품명 {i+1}"
            }
            
            expected_response = {
                "message": "상품명이 성공적으로 수정되었습니다.",
                "compayny_goods_cd": product["compayny_goods_cd"],
                "old_name": product["product_nm"],
                "new_name": f"수정된 상품명 {i+1}"
            }
            
            mock_update_service.modify_product_name.return_value = expected_response
            
            # When: API 요청 실행
            response = client.put("/api/v1/product/name", json=request_data)
            
            # Then: 응답 검증
            assert response.status_code == 200
            response_data = response.json()
            
            # Mock DB 데이터와 일치하는지 확인
            assert response_data["compayny_goods_cd"] == product["compayny_goods_cd"]
            assert response_data["old_name"] == product["product_nm"]
            assert response_data["new_name"] == f"수정된 상품명 {i+1}"
            
            # Mock 호출 확인
            mock_update_service.modify_product_name.assert_called_with(
                compayny_goods_cd=product["compayny_goods_cd"],
                product_name=f"수정된 상품명 {i+1}"
            ) 