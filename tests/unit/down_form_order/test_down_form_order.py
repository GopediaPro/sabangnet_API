"""
다운폼 주문 API 테스트
"""
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.logs.sabangnet_logger import get_logger
from unittest.mock import AsyncMock, MagicMock, patch

from api.v1.endpoints.down_form_order import get_data_processing_usecase
from api.v1.endpoints.down_form_order import get_down_form_order_create_service
from api.v1.endpoints.down_form_order import get_down_form_order_read_service
from api.v1.endpoints.down_form_order import get_down_form_order_update_service
from api.v1.endpoints.down_form_order import get_down_form_order_delete_service


logger = get_logger(__name__)


@pytest.mark.api
class TestDownFormOrderAPI:
    """다운폼 주문 API 테스트 클래스"""

    def test_get_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 목록 조회 테스트"""
        try:
            logger.info("다운폼 주문 목록 조회 테스트 시작")
            
            mock_orders = []
            mock_service = MagicMock()
            mock_service.get_down_form_orders = AsyncMock(return_value=mock_orders)
            
            test_app.dependency_overrides[get_down_form_order_read_service] = lambda: mock_service
            
            try:
                response = async_client.get("/api/v1/down-form-order")
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert isinstance(data["items"], list)
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 목록 조회 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 목록 조회 테스트 실패: {e}")
            raise e

    def test_get_down_form_orders_pagination(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 페이징 조회 테스트"""
        try:
            logger.info("다운폼 주문 페이징 조회 테스트 시작")
            
            mock_service = MagicMock()
            mock_service.get_down_form_orders_by_pagenation = AsyncMock(return_value=([], 0))
            
            test_app.dependency_overrides[get_down_form_order_read_service] = lambda: mock_service
            
            try:
                response = async_client.get("/api/v1/down-form-order/pagination?page=1&page_size=10")
                
                assert response.status_code == 200
                data = response.json()
                assert "total" in data
                assert "page" in data
                assert "page_size" in data
                assert "items" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 페이징 조회 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 페이징 조회 테스트 실패: {e}")
            raise e

    def test_bulk_create_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 벌크 생성 테스트"""
        try:
            logger.info("다운폼 주문 벌크 생성 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "idx": "TEST_ORDER_001",
                        "order_id": "MALL_ORDER_001",
                        "product_name": "테스트상품1",
                        "sale_cnt": 1,
                        "pay_cost": 12000,
                        "receive_name": "홍길동"
                    }
                ]
            }
            
            mock_service = MagicMock()
            mock_service.bulk_create_down_form_orders = AsyncMock(return_value=1)
            
            test_app.dependency_overrides[get_down_form_order_create_service] = lambda: mock_service
            
            try:
                response = async_client.post("/api/v1/down-form-order/bulk", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 1
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 벌크 생성 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 벌크 생성 테스트 실패: {e}")
            raise e

    def test_bulk_update_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 벌크 수정 테스트"""
        try:
            logger.info("다운폼 주문 벌크 수정 테스트 시작")
            
            test_data = {
                "items": [
                    {
                        "id": 1,
                        "idx": "TEST_ORDER_001",
                        "order_id": "MALL_ORDER_001",
                        "product_name": "수정된상품1",
                        "sale_cnt": 2,
                        "pay_cost": 15000,
                        "receive_name": "김철수"
                    }
                ]
            }
            
            mock_service = MagicMock()
            mock_service.bulk_update_down_form_orders = AsyncMock(return_value=1)
            
            test_app.dependency_overrides[get_down_form_order_update_service] = lambda: mock_service
            
            try:
                response = async_client.put("/api/v1/down-form-order/bulk", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 1
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 벌크 수정 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 벌크 수정 테스트 실패: {e}")
            raise e

    def test_bulk_delete_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 벌크 삭제 테스트"""
        try:
            logger.info("다운폼 주문 벌크 삭제 테스트 시작")
            
            test_data = {
                "ids": [1, 2, 3]
            }
            
            mock_service = MagicMock()
            mock_service.bulk_delete_down_form_orders = AsyncMock(return_value=3)
            
            test_app.dependency_overrides[get_down_form_order_delete_service] = lambda: mock_service
            
            try:
                import json
                response = async_client.request("DELETE", "/api/v1/down-form-order/bulk", json=test_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert len(data["items"]) == 3
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 벌크 삭제 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 벌크 삭제 테스트 실패: {e}")
            raise e

    def test_delete_all_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 전체 삭제 테스트"""
        try:
            logger.info("다운폼 주문 전체 삭제 테스트 시작")
            
            mock_service = MagicMock()
            mock_service.delete_all_down_form_orders = AsyncMock(return_value=None)
            
            test_app.dependency_overrides[get_down_form_order_delete_service] = lambda: mock_service
            
            try:
                response = async_client.delete("/api/v1/down-form-order/all")
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                assert data["message"] == "모든 데이터 삭제 완료"
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 전체 삭제 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 전체 삭제 테스트 실패: {e}")
            raise e

    def test_delete_duplicate_down_form_orders(self, test_app: FastAPI, async_client: TestClient):
        """다운폼 주문 중복 삭제 테스트"""
        try:
            logger.info("다운폼 주문 중복 삭제 테스트 시작")
            
            mock_service = MagicMock()
            mock_service.delete_duplicate_down_form_orders = AsyncMock(return_value=None)
            
            test_app.dependency_overrides[get_down_form_order_delete_service] = lambda: mock_service
            
            try:
                response = async_client.delete("/api/v1/down-form-order/duplicate")
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                
            finally:
                test_app.dependency_overrides = {}
                
            logger.info("다운폼 주문 중복 삭제 테스트 완료")
        except Exception as e:
            logger.error(f"다운폼 주문 중복 삭제 테스트 실패: {e}")
            raise e

    def test_excel_to_db(self, test_app: FastAPI, async_client: TestClient):
        """엑셀 파일을 DB로 변환 테스트"""
        try:
            logger.info("엑셀 파일을 DB로 변환 테스트 시작")
            
            test_file_content = b"test excel content"
            
            mock_usecase = MagicMock()
            mock_usecase.process_excel_to_down_form_orders = AsyncMock(return_value=10)
            
            test_app.dependency_overrides[get_data_processing_usecase] = lambda: mock_usecase
            
            # ExcelHandler 모킹
            with patch('utils.excels.excel_handler.ExcelHandler.from_upload_file_to_dataframe') as mock_excel:
                mock_excel.return_value = MagicMock()  # DataFrame 모킹
                
                try:
                    files = {"file": ("test.xlsx", test_file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    data = {"template_code": "test_template"}
                    
                    response = async_client.post("/api/v1/down-form-order/excel-to-db", files=files, data=data)
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "saved_count" in data
                    assert data["saved_count"] == 10
                    
                finally:
                    test_app.dependency_overrides = {}
                    
            logger.info("엑셀 파일을 DB로 변환 테스트 완료")
        except Exception as e:
            logger.error(f"엑셀 파일을 DB로 변환 테스트 실패: {e}")
            raise e
