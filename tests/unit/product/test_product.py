"""
상품 API 테스트
"""
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from unittest.mock import AsyncMock, MagicMock
from utils.logs.sabangnet_logger import get_logger

from api.v1.endpoints.product import get_product_read_service
from api.v1.endpoints.product import get_product_update_service

from api.v1.endpoints.product import get_product_db_xml_usecase
from api.v1.endpoints.product import get_product_create_db_to_excel_usecase

logger = get_logger(__name__)


@pytest.mark.api
class TestProductAPI:
    """상품 API 테스트 클래스"""

    def test_db_to_xml_sabangnet_request_all_success(self, test_app: FastAPI, async_client: TestClient):
        """DB to XML 사방넷 요청 전체 성공 테스트"""
        try:
            logger.info("DB to XML 사방넷 요청 전체 성공 테스트 시작")
            
            mock_xml_path = "/tmp/test.xml"
            mock_object_name = "test.xml"
            mock_xml_url = "http://minio.test.com/test.xml"
            mock_response_xml = "<response><success>true</success></response>"
            mock_product_ids = [("GOODS001", 1001), ("GOODS002", 1002)]
            
            mock_usecase = MagicMock()
            mock_usecase.db_to_xml_file_all = AsyncMock(return_value=mock_xml_path)
            mock_usecase.get_product_raw_data_count = AsyncMock(return_value=10)
            mock_usecase.update_product_id_by_compayny_goods_cd = AsyncMock(return_value=None)
            
            test_app.dependency_overrides[get_product_db_xml_usecase] = lambda: mock_usecase
            
            # MinIO 관련 모킹
            with MagicMock() as mock_minio_upload, MagicMock() as mock_minio_url, MagicMock() as mock_request, MagicMock() as mock_parse:
                mock_minio_upload.return_value = mock_object_name
                mock_minio_url.return_value = mock_xml_url
                mock_request.return_value = mock_response_xml
                mock_parse.return_value = mock_product_ids
                
                try:
                    response = async_client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "success" in data
                    assert data["success"] is True
                    assert "xml_file_path" in data
                    assert "processed_count" in data
                    
                finally:
                    test_app.dependency_overrides = {}
                    
            logger.info("DB to XML 사방넷 요청 전체 성공 테스트 완료")
        except Exception as e:
            logger.error(f"DB to XML 사방넷 요청 전체 성공 테스트 실패: {e}")
            raise e

    def test_db_to_xml_sabangnet_request_all_no_data(self, test_app: FastAPI, async_client: TestClient):
        """DB to XML 사방넷 요청 전체 - 데이터 없음 테스트"""
        try:
            logger.info("DB to XML 사방넷 요청 전체 - 데이터 없음 테스트 시작")
            
            mock_usecase = MagicMock()
            mock_usecase.db_to_xml_file_all = AsyncMock(side_effect=ValueError("데이터가 없습니다"))
            
            test_app.dependency_overrides[get_product_db_xml_usecase] = lambda: mock_usecase
            
            try:
                response = async_client.post("/api/v1/product/db-to-xml-all/sabangnet-request")
                
                assert response.status_code == 404
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("DB to XML 사방넷 요청 전체 - 데이터 없음 테스트 완료")
        except Exception as e:
            logger.error(f"DB to XML 사방넷 요청 전체 - 데이터 없음 테스트 실패: {e}")
            raise e

    def test_excel_to_xml_n8n_test_success(self, test_app: FastAPI, async_client: TestClient):
        """엑셀 to XML n8n 테스트 성공 테스트"""
        try:
            logger.info("엑셀 to XML n8n 테스트 성공 테스트 시작")
            
            test_data = {
                "fileName": "test_file.xlsx",
                "sheetName": "Sheet1"
            }
            
            mock_xml_path = "/tmp/test.xml"
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            
            # ProductCreateService 모킹
            with MagicMock() as mock_excel_to_xml, MagicMock() as mock_requests_post:
                mock_excel_to_xml.return_value = mock_xml_path
                mock_requests_post.return_value = mock_response
                
                response = async_client.post("/api/v1/product/excel-to-xml-n8n-test", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "success" in data
                
            logger.info("엑셀 to XML n8n 테스트 성공 테스트 완료")
        except Exception as e:
            logger.error(f"엑셀 to XML n8n 테스트 성공 테스트 실패: {e}")
            raise e

    def test_excel_to_xml_n8n_test_file_not_found(self, async_client: TestClient):
        """엑셀 to XML n8n 테스트 파일 없음 테스트"""
        try:
            logger.info("엑셀 to XML n8n 테스트 파일 없음 테스트 시작")
            
            test_data = {
                "fileName": "nonexistent_file.xlsx",
                "sheetName": "Sheet1"
            }
            
            # ProductCreateService 모킹
            with MagicMock() as mock_excel_to_xml:
                mock_excel_to_xml.side_effect = FileNotFoundError("파일을 찾을 수 없습니다")
                
                response = async_client.post("/api/v1/product/excel-to-xml-n8n-test", json=test_data)
                
                assert response.status_code == 404
                data = response.json()
                assert "detail" in data
                
            logger.info("엑셀 to XML n8n 테스트 파일 없음 테스트 완료")
        except Exception as e:
            logger.error(f"엑셀 to XML n8n 테스트 파일 없음 테스트 실패: {e}")
            raise e

    def test_modify_product_name_success(self, test_app: FastAPI, async_client: TestClient):
        """상품명 수정 성공 테스트"""
        try:
            logger.info("상품명 수정 성공 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": "GOODS001",
                "name": "수정된상품명"
            }
            
            mock_dto = {
                "id": 1,
                "compayny_goods_cd": "GOODS001",
                "product_name": "수정된상품명"
            }
            
            mock_service = MagicMock()
            mock_service.modify_product_name = AsyncMock(return_value=mock_dto)
            
            test_app.dependency_overrides[get_product_update_service] = lambda: mock_service
            
            try:
                response = async_client.put("/api/v1/product/name", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["product_name"] == "수정된상품명"
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("상품명 수정 성공 테스트 완료")
        except Exception as e:
            logger.error(f"상품명 수정 성공 테스트 실패: {e}")
            raise e

    def test_modify_product_name_invalid_request(self, async_client: TestClient):
        """상품명 수정 잘못된 요청 테스트"""
        try:
            logger.info("상품명 수정 잘못된 요청 테스트 시작")
            
            # 필수 필드가 없는 요청
            test_data = {}
            
            response = async_client.put("/api/v1/product/name", json=test_data)
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("상품명 수정 잘못된 요청 테스트 완료")
        except Exception as e:
            logger.error(f"상품명 수정 잘못된 요청 테스트 실패: {e}")
            raise e

    def test_modify_product_name_not_found(self, test_app: FastAPI, async_client: TestClient):
        """상품명 수정 상품 없음 테스트"""
        try:
            logger.info("상품명 수정 상품 없음 테스트 시작")
            
            test_data = {
                "compayny_goods_cd": "NONEXISTENT",
                "name": "수정된상품명"
            }
            
            mock_service = MagicMock()
            mock_service.modify_product_name = AsyncMock(side_effect=ValueError("상품을 찾을 수 없습니다"))
            
            test_app.dependency_overrides[get_product_update_service] = lambda: mock_service
            
            try:
                response = async_client.put("/api/v1/product/name", json=test_data)
                
                assert response.status_code == 404
                data = response.json()
                assert "detail" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("상품명 수정 상품 없음 테스트 완료")
        except Exception as e:
            logger.error(f"상품명 수정 상품 없음 테스트 실패: {e}")
            raise e

    def test_get_products_success(self, test_app: FastAPI, async_client: TestClient):
        """상품 목록 조회 성공 테스트"""
        try:
            logger.info("상품 목록 조회 성공 테스트 시작")
            
            mock_products = [
                {
                    "id": 1,
                    "compayny_goods_cd": "GOODS001",
                    "product_name": "테스트상품1"
                },
                {
                    "id": 2,
                    "compayny_goods_cd": "GOODS002",
                    "product_name": "테스트상품2"
                }
            ]
            
            mock_service = MagicMock()
            mock_service.get_products = AsyncMock(return_value=mock_products)
            
            test_app.dependency_overrides[get_product_read_service] = lambda: mock_service
            
            try:
                response = async_client.get("/api/v1/product?page=1&page_size=10")
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 2
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("상품 목록 조회 성공 테스트 완료")
        except Exception as e:
            logger.error(f"상품 목록 조회 성공 테스트 실패: {e}")
            raise e

    def test_bulk_db_to_excel_success(self, test_app: FastAPI, async_client: TestClient):
        """벌크 DB to Excel 성공 테스트"""
        try:
            logger.info("벌크 DB to Excel 성공 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "compayny_goods_cd": "GOODS001",
                        "product_name": "테스트상품1"
                    },
                    {
                        "compayny_goods_cd": "GOODS002",
                        "product_name": "테스트상품2"
                    }
                ]
            }
            
            mock_excel_path = "/tmp/test.xlsx"
            mock_service = MagicMock()
            mock_service.bulk_db_to_excel = AsyncMock(return_value=mock_excel_path)
            
            test_app.dependency_overrides[get_product_create_db_to_excel_usecase] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/product/bulk-db-to-excel", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "excel_file_path" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("벌크 DB to Excel 성공 테스트 완료")
        except Exception as e:
            logger.error(f"벌크 DB to Excel 성공 테스트 실패: {e}")
            raise e

    def test_get_products_invalid_page(self, async_client: TestClient):
        """상품 목록 조회 잘못된 페이지 테스트"""
        try:
            logger.info("상품 목록 조회 잘못된 페이지 테스트 시작")
            
            # 잘못된 페이지 번호
            response = async_client.get("/api/v1/product?page=-1&page_size=10")
            
            assert response.status_code == 422  # Validation Error
            
            logger.info("상품 목록 조회 잘못된 페이지 테스트 완료")
        except Exception as e:
            logger.error(f"상품 목록 조회 잘못된 페이지 테스트 실패: {e}")
            raise e 